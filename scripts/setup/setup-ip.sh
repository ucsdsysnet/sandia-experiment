#!/bin/bash

. scripts/setup/ip_interface.config

NIC_TYPE=$nic_type
HOST_TYPE=$host_type

for arg in "$@"
do
case $arg in
    -n|--nictype)
        shift
        NIC_TYPE=$1
        shift
        ;;
    -h|--hosttype)
        shift
        HOST_TYPE=$1
        shift
        ;;
    --assign-multiple-ips)
        shift
        ASSING_MULTIPLE_IPS=1
        ;;
esac
done

setup_ip()
{
    [[ $ASSING_MULTIPLE_IPS -eq 1 ]] && MAX_IP=32 || MAX_IP=0
        for i in $(seq 0 $MAX_IP); do
            # echo $1.$2.$3.$(($4 + $i))/$network_prefix_len $5
            sudo ip addr add $1.$2.$3.$(($4 + $i))/$network_prefix_len dev $5
        done
}

main()
{
    echo $NIC_TYPE $HOST_TYPE
    if [[ $NIC_TYPE = "fpga" ]]; then
        ip addr show $FPGA_IFACE | grep "inet " | awk '{print $2}' | xargs -I {} sudo ip addr del {} dev $FPGA_IFACE
        echo "fpga"
        if [[ $HOST_TYPE = "src" ]]; then
            echo "src"
            IFS='.' read ip1 ip2 ip3 ip4 <<< "$FPGA_src_ip"
            setup_ip $ip1 $ip2 $ip3 $ip4 $FPGA_IFACE
        elif [[ $HOST_TYPE = "dst" ]]; then
            echo "dst"
            IFS='.' read ip1 ip2 ip3 ip4 <<< "$FPGA_dst_ip"
            setup_ip $ip1 $ip2 $ip3 $ip4 $FPGA_IFACE
        fi
    else
        ip addr show $cx5_IFACE | grep "inet " | awk '{print $2}' | xargs -I {} sudo ip addr del {} dev $cx5_IFACE
        echo "cx5"
        if [[ $HOST_TYPE = "src" ]]; then
            echo "src"
            IFS='.' read ip1 ip2 ip3 ip4 <<< "$cx5_src_ip"
            setup_ip $ip1 $ip2 $ip3 $ip4 $cx5_IFACE
        elif [[ $HOST_TYPE = "dst" ]]; then
            echo "dst"
            IFS='.' read ip1 ip2 ip3 ip4 <<< "$cx5_dst_ip"
            setup_ip $ip1 $ip2 $ip3 $ip4 $cx5_IFACE
        fi
    fi
}

main 
