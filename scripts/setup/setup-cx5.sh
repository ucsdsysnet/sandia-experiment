#!/bin/zsh

cd "$(dirname "$0")"

. ../shared.sh
IFACE=$(get_cx5_iface)

declare -A HOST2IP=(
    ["yeti-04"]="192.168.1.4"
    ["yeti-01"]="192.168.1.1"
)

declare -A HOST2MAC=(
    ["yeti-04"]="ec:0d:9a:68:21:a8"
    ["yeti-01"]="ec:0d:9a:68:21:88"
)

MY_HOST=$(hostname -s)
MTU=1500

# This function for some reason doesn't work in bash ...
regex() {
    gawk 'match($0,/'$1'/, ary) {print ary['${2:-'0'}']}';
}

set_ip()
{
    MY_IP=${HOST2IP[$MY_HOST]}
    if [ -z "$MY_IP" ]; then
        echo >&2 "Host not found in IP mapping"
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

set_mellanox_cx5_pci_settings()
{
    pcidevice=$(lspci | grep -i ethernet | grep "ConnectX-5" | cut -d' ' -f 1)
    maxreadreq_size=$(sudo lspci -s $pcidevice -vvv | grep MaxReadReq | regex 'MaxReadReq ([0-9]+) bytes' 1)
    if [[ $maxreadreq_size -lt 4096 ]]; then
        echo "Current MaxReadReq is $maxreadreq_size, setting to 4096 ..."
        # This number came from https://certification.canonical.com/cert-notes/network-tuning/
        # There used to be a Mellanox article that explains why it's 5936, but it can no longer be found.
        # Bit masking as suggested by alexforencich
        sudo setpci -s $pcidevice CAP_EXP+8.w=5000:7000
    fi
    maxreadreq_size=$(sudo lspci -s $pcidevice -vvv | grep MaxReadReq | regex 'MaxReadReq ([0-9]+) bytes' 1)
    echo "Current MaxReadReq is $maxreadreq_size"
    echo "Done"
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

mellanox_perf_tuning()
{
    echo "Applying Mellanox performance tuning ..."
    # 3.1 IRQ Affinity
    sudo /etc/init.d/irqbalance stop

    # ******** READ THIS ********
    # Manuall check: If all the rows are “fffff” or “00000”, it means it did not work and the irqbalance needs to be restarted.
    echo >&2
    echo >&2 "******** PLEASE manually check below ********"
    echo >&2 "If all the rows are “fffff” or “00000”, it means it did not work and the irqbalance needs to be restarted."
    echo >&2
    show_irq_affinity.sh $IFACE
    # 3.1.2
    nic_local_numa_node=$(cat /sys/class/net/$IFACE/device/numa_node)
    sudo set_irq_affinity_bynode.sh $nic_local_numa_node $IFACE

    # 3.4 NUMA tuning
    numa_local_cpulist=$(cat /sys/devices/system/node/node$nic_local_numa_node/cpulist)
    # Pin to NIC-local numa node like this:
    taskset -c $numa_local_cpulist echo "Pin to NIC-local numa node like this"

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
    # sudo ip link set $IFACE mtu 9000
    sudo ethtool -K $IFACE ntuple on
}

main()
{
    # sudo ip link set $IFACE up
    # set_ip
    # sudo ip link set $IFACE mtu $MTU

    # set_mlnx_qos
    set_mellanox_cx5_pci_settings
    reset_nic_irq_mapping
    mellanox_perf_tuning
    sigcomm21_host_network_stack_optimization
    # Explicitly turning off TSO for now, for fair comparison between CX-5 and Corundum
    sudo ethtool -K $IFACE tso off
    sudo ethtool -K $IFACE gso on
}

main

