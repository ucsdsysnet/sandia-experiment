#!/bin/bash

cd "$(dirname "$0")"

source ../shared.sh
IFACE=$(get_iface)

# Source host:

# See multiq in https://man7.org/linux/man-pages/man8/tc.8.html
echo "Switching to multiq for direct access to hardware queues ..."
sudo tc qdisc del dev $IFACE root
sudo tc qdisc add dev $IFACE handle 1 root multiq

# See queue_mapping in https://man7.org/linux/man-pages/man8/tc-skbedit.8.html
echo "Adding skbedit rules for explicit TX queue mapping ..."
sudo tc filter del dev $IFACE
for i in {1..32}; do
    sudo tc filter add dev $IFACE protocol ip parent 1: prio 0 u32 \
                    match ip dst 10.0.0.$(echo "200 + $i" | bc) \
                    action skbedit queue_mapping $i
done
