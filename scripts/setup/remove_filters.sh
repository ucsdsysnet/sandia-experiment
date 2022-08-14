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

remove_clsact()
{
    sudo tc filter del dev $1 egress
    sudo tc qdisc del dev $1 clsact
}

main()
{
    echo $NIC_TYPE
    if [[ $NIC_TYPE = "fpga" ]]; then
        echo "fpga"
        remove_clsact $FPGA_IFACE 
    else
        remove_clsact $cx5_IFACE
    fi
}

main