#!/bin/bash

cd "$(dirname "$0")"

source ../shared.sh
IFACE=$(get_iface)
IFACE_CX5=$(get_cx5_iface)
[[ "$IFACE" == "$IFACE_CX5" ]] && ip_octet3=1 || ip_octet3=2

for arg in "$@"
do
case $arg in
    --enable-tc-mapping)
        shift
        ENABLE_TC_MAPPING=1
        ;;
esac
done

# Source host:

sudo ip link set $IFACE up
ip addr show $IFACE | grep "inet " | awk '{print $2}' | xargs -I {} sudo ip addr del {} dev $IFACE
sudo ip addr add 10.0.$ip_octet3.100/22 dev $IFACE

# See multiq in https://man7.org/linux/man-pages/man8/tc.8.html
echo "Reseting qdisc to default ..."
sudo tc qdisc del dev $IFACE root
if [[ $ENABLE_TC_MAPPING -eq 1 ]]; then
    echo "Switching to multiq for direct access to hardware queues ..."
    sudo tc qdisc add dev $IFACE handle 1 root multiq
fi

# See queue_mapping in https://man7.org/linux/man-pages/man8/tc-skbedit.8.html
echo "Removing existing TC filters ..."
filter_count=$(tc filter show dev ens4 | wc -l)
[[ filter_count -gt 0 ]] && sudo tc filter del dev $IFACE
if [[ $ENABLE_TC_MAPPING -eq 1 ]]; then
    echo "Adding skbedit rules for explicit TX queue mapping ..."
    for i in {1..32}; do
        sudo tc filter add dev $IFACE protocol ip parent 1: prio 0 u32 \
                        match ip dst 10.0.$ip_octet3.$(echo "200 + $i" | bc) \
                        action skbedit queue_mapping $i
    done
fi
