#!/bin/bash

. scripts/setup/ip_interface.config

NIC_TYPE=$nic_type
HOST_TYPE=$host_type

for arg in "$@"
do
case $arg in
    -t|--nictype)
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

if [[ $NIC_TYPE -eq "fpga" ]]; then
    # ip addr show $IFACE | grep "inet " | awk '{print $2}' | xargs -I {} sudo ip addr del {} dev $IFACE
    echo $NIC_TYPE
    if [[ $HOST_TYPE -eq "src" ]]; then
        echo $HOST_TYPE
    elif [[ $HOST_TYPE -eq "dst" ]]; then
        echo $HOST_TYPE
    fi
else
    # ip addr show $IFACE | grep "inet " | awk '{print $2}' | xargs -I {} sudo ip addr del {} dev $IFACE
    echo $NIC_TYPE
    if [[ $HOST_TYPE -eq "src" ]]; then
        echo $HOST_TYPE
    elif [[ $HOST_TYPE -eq "dst" ]]; then
        echo $HOST_TYPE
    fi
fi
