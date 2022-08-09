#!/bin/zsh

cd "$(dirname "$0")"

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

enable_hyperthreading()
{
    # Enable Hyper-Threading
    echo "Enabling Hyper-Threading ..."
    smt_active=$(cat /sys/devices/system/cpu/smt/active)
    if [[ $smt_active -eq 0 ]]; then
        echo "SMT currently inactive, turning on..."
        echo on | sudo tee /sys/devices/system/cpu/smt/control
        [[ $(cat /sys/devices/system/cpu/smt/active) -eq 1 ]] || echo >&2 "[Warning] Failed to turn on SMT."
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

tcp_settings()
{
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

main()
{
    tcp_settings
    # performance tuning
    set_cpu_high_performance
    # disable_hyperthreading
    enable_hyperthreading
    disable_daemon_processes
}

main