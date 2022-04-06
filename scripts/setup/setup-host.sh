#!/bin/bash

cd "$(dirname "$0")"

declare -A HOST2IP=(
    ["yeti-02"]="10.0.0.2"
    ["yeti-04"]="10.0.0.101"
    ["yak-03"]="10.0.0.102"
)

declare -A HOST2MAC=(
    ["yeti-02"]="ec:0d:9a:68:21:b0"
    ["yeti-04"]="ec:0d:9a:68:21:a8"
    ["yak-03"]="ec:0d:9a:68:21:c0"
)

get_iface()
{
    echo "$(ibdev2netdev | cut -f5 -d' ')"
    # echo "$(ibdev2netdev | grep 'mlx5' | regex 'mlx5.* port .* ==> (\w+)' 1)"
}

IFACE=$(get_iface)
MY_HOST=$(hostname -s)
MTU=1500


set_ip()
{
    MY_IP=${HOST2IP[$MY_HOST]}
    MY_MAC=${HOST2MAC[$MY_HOST]}
    if [ -z "$MY_IP" ] || [ -z "$MY_MAC" ]; then
        echo >&2 "Host not found in IP or MAC mapping"
        return 1
    fi

    # delete existing IPs
    ip addr show $IFACE | grep "inet " | awk '{print $2}' | xargs -I {} sudo ip addr del {} dev $IFACE

    sudo ip addr add $MY_IP/32 dev $IFACE
    ACTUAL_IP=$(ip addr show $IFACE | grep "inet " | awk '{print $2}')
    if [ "$MY_IP/32" != "$ACTUAL_IP" ]; then
        echo >&2 "Failed to set IP to $MY_IP. Got $ACTUAL_IP instead."
        return 1
    fi
}

run_arp()
{
    for H in ${!HOST2IP[@]}
    do
        MY_HOST=$(hostname -s)
        if [ $H = $MY_HOST ]; then
            continue
        fi

        IP=${HOST2IP[$H]}
        MAC=${HOST2MAC[$H]}
        sudo arp -s $IP $MAC
    done
}

set_mlnx_qos()
{
    sudo cma_roce_tos -d mlx5_0 -t 0
    sudo mlnx_qos -i $IFACE -p 0,1,2,3,4,5,6,7 \
                    -f 1,1,0,0,0,0,0,0 \
                    --buffer_size 261632,261632,0,0,0,0,0,0 \
                    --dscp2prio='set,1,1'
}

set_cpu_high_performance()
{
    # Set CPU frequency to max
    echo "Setting CPU governor to performance ..."
    if ! dpkg -s cpufrequtils 2>&1 | grep -q 'installed$'; then
        echo "Package cpufrequtils not installed. Installing ..."
        sudo apt-get install -y cpufrequtils
    fi
    echo 'GOVERNOR="performance"' | sudo tee /etc/default/cpufrequtils > /dev/null
    sudo cpufreq-set -r -g performance
    # It seems that we also need to manually set it for each CPU
    echo performance | sudo tee /sys/devices/system/cpu/cpu*/cpufreq/scaling_governor
    sudo systemctl disable ondemand
    echo "Done"
    echo
}

disable_hyperthreading()
{
    # Disable Hyper-Threading
    echo "Disabling Hyper-Threading ..."
    # CPU_CORE_COUNT=20
    # from=$((CPU_CORE_COUNT))
    # to=$((2 * CPU_CORE_COUNT - 1))
    # for i in $(seq $from $to); do
    #     echo 0 | sudo tee --append /sys/devices/system/cpu/cpu$i/online > /dev/null
    #     cat "/sys/devices/system/cpu/cpu$i/online"
    # done
    # max_cpu=$((CPU_CORE_COUNT - 1))
    # if ! lscpu | grep -q "On-line CPU(s) list:  0-$max"; then
    #     echo "[Warning] HT not disabled correctly."
    # fi
    smt_active=$(cat /sys/devices/system/cpu/smt/active)
    if [[ $smt_active -eq 1 ]]; then
        echo "SMT currently active, turning off..."
        echo off | sudo tee /sys/devices/system/cpu/smt/control
        [[ $(cat /sys/devices/system/cpu/smt/active) -eq 0 ]] || echo >&2 "[Warning] Failed to turn off SMT."
    fi
    echo "Done"
    echo
}

reset_nic_irq_mapping()
{
    # Restart NIC driver to update interrupt handler mapping
    echo "Restarting NIC driver to update IRQ mapping ..."
    sudo /etc/init.d/openibd restart
    sleep 5
    irq_count=$(cat /proc/interrupts | grep $IFACE- | wc -l)
    core_count=$(nproc)
    if [[ $irq_count -ne $core_count ]]; then
        echo "[Warning] NIC IRQ count not equal to CPU count."
    fi
    echo "Done"
    echo
}

disable_daemon_processes()
{
    echo "Disabling daemon processes ..."
    sudo service cron stop
    sudo service atd stop
    sudo service iscdis stop
    sudo service irqbalance stop
    echo "Done"
    echo
}

set_mellanox_cx5_pci_settings()
{
    pcidevice=$(lspci | grep -i ethernet | grep "ConnectX-5" | cut -d' ' -f 1)
    maxreadreq_size=$(sudo lspci -s $pcidevice -vvv | grep MaxReadReq | regex 'MaxReadReq ([0-9]+) bytes' 1)
    if [[ $maxreadreq_size -lt 4096 ]]; then
        echo "Current MaxReadReq is $maxreadreq_size, setting to 4096 ..."
        # This number came from https://certification.canonical.com/cert-notes/network-tuning/
        # There used to be a Mellanox article that explains why it's 5936, but it can no longer be found.
        sudo setpci -s $pcidevice 68.w=5936
    fi
    maxreadreq_size=$(sudo lspci -s $pcidevice -vvv | grep MaxReadReq | regex 'MaxReadReq ([0-9]+) bytes' 1)
    echo "Current MaxReadReq is $maxreadreq_size"
    echo "Done"
}

mellanox_perf_tuning()
{
    echo "Applying Mellanox performance tuning ..."
    # 3.1 IRQ Affinity
    sudo /etc/init.d/irqbalance stop
    # Manuall check: If all the rows are “fffff” or “00000”, it means it did not work and the irqbalance needs to be restarted.
    show_irq_affinity.sh $IFACE
    # 3.1.2
    nic_local_numa_node=$(cat /sys/class/net/$IFACE/device/numa_node)
    set_irq_affinity_bynode.sh $nic_local_numa_node $IFACE

    # 3.4 NUMA tuning
    numa_local_cpulist=$(cat /sys/devices/system/node/node$nic_local_numa_node/cpulist)
    # Pin to NIC-local numa node like this:
    taskset -c $numa_local_cpulist ls

    # 3.9 sysctl tuning
    sudo sysctl -w net.ipv4.tcp_timestamps=0
    sudo sysctl -w net.ipv4.tcp_sack=1
    sudo sysctl -w net.core.netdev_max_backlog=250000
    sudo sysctl -w net.core.rmem_max=2147483647
    sudo sysctl -w net.core.wmem_max=2147483647
    sudo sysctl -w net.core.rmem_default=4194304
    sudo sysctl -w net.core.wmem_default=4194304
    sudo sysctl -w net.core.optmem_max=4194304
    sudo sysctl -w net.ipv4.tcp_rmem="4096 87380 2147483647"
    sudo sysctl -w net.ipv4.tcp_wmem="4096 65536 2147483647"
    sudo sysctl -w net.ipv4.tcp_low_latency=1
    sudo sysctl -w net.ipv4.tcp_adv_win_scale=1
}

sigcomm21_host_network_stack_optimization()
{
    # Source: https://www.cs.cornell.edu/~ragarwal/pubs/network-stack.pdf
    sudo ethtool -K $IFACE tso on
    sudo ethtool -K $IFACE gro on
    sudo ethtool -K $IFACE lro off
    sudo ip link set $IFACE mtu 9000
    sudo ethtool -K $IFACE ntuple on
}

main()
{
    sudo ip link set $IFACE up
    set_ip
    # run_arp
    # sudo ethtool --set-priv-flags $IFACE sniffer off
    sudo ip link set $IFACE mtu $MTU
    # set_mlnx_qos

    # performance tuning
    set_cpu_high_performance
    disable_hyperthreading
    set_mellanox_cx5_pci_settings
    reset_nic_irq_mapping
    disable_daemon_processes
    mellanox_perf_tuning
    sigcomm21_host_network_stack_optimization
}

# set -e
#set -x
main

