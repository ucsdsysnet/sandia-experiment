#!/bin/bash

parallelism=1

for arg in "$@"
do
case $arg in
    -p|--parallel)
        shift
        parallelism=$1
        shift
        ;;
esac
done

source ../shared.sh
IFACE=$(get_iface)

nic_local_numa_node=$(cat /sys/class/net/$IFACE/device/numa_node)

for i in $(seq 1 $parallelism);
do
    port=$(echo "5100+$i" | bc)
    numactl -N $nic_local_numa_node iperf3 -s -p $port &
done
