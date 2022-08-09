#!/bin/bash

. scripts/setup/ip_interface.config

NIC_TYPE=$nic_type

for arg in "$@"
do
case $arg in
    -n|--nictype)
        shift
        NIC_TYPE=$1
        shift
        ;;
esac
done

settings()
{
    sudo ip link set $1 mtu $MTU
    sudo ethtool -K $1 gso on
    # sudo ip link set $1 up
}

main()
{
    echo $NIC_TYPE
    if [[ $NIC_TYPE = "fpga" ]]; then
        echo "fpga"
        settings $FPGA_IFACE 
    else
        settings $cx5_IFACE
    fi
}

main