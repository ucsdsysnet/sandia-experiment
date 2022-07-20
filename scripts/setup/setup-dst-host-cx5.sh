#!/bin/bash

cd "$(dirname "$0")"

TOTAL_IP_GROUPS=1

source ../shared.sh
IFACE=$(get_cx5_iface)
ip_octet3_dst=20

for arg in "$@"
do
case $arg in
    --assign-multiple-ips)
        shift
        ASSING_MULTIPLE_IPS=1
        ;;
esac
done

sudo ip link set $IFACE up

# (optional) delete existing IPs
ip addr show $IFACE | grep "inet " | awk '{print $2}' | xargs -I {} sudo ip addr del {} dev $IFACE

# Destination host:
[[ $ASSING_MULTIPLE_IPS -eq 1 ]] && MAX_IP=32 || MAX_IP=0
# for j in $(seq 1 $TOTAL_IP_GROUPS); do
    # ip_octet2=$j
    for i in $(seq 0 $MAX_IP); do
        sudo ip addr add 10.10.$ip_octet3_dst.$((100 + $i))/16 dev $IFACE
    done
# done