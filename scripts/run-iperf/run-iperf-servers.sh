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

for i in $(seq 1 $parallelism);
do
    port=$(echo "5100+$i" | bc)
    numactl -N 1 iperf3 -s -p $port &
done
