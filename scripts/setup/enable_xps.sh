#!/bin/bash

. scripts/setup/ip_interface.config

NIC_TYPE=$nic_type

cd "$(dirname "$0")"

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

enable_xps()
{
    nic_local_numa_node=$(cat /sys/class/net/$1/device/numa_node)
    sudo set_irq_affinity_bynode.sh $nic_local_numa_node $1
}

main()
{
    if [[ $NIC_TYPE = "fpga" ]]; then
        enable_xps $FPGA_IFACE
    else
        enable_xps $cx5_IFACE
    fi 
}

main