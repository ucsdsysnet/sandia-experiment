#!/bin/bash

cd "$(dirname "$0")"

source ../shared.sh
IFACE=$(get_corundum_iface)
ip_octet3_src=10
ip_octet3_dst=20
network_prefix='10.100'
network_prefix_len=16

sudo tc qdisc del dev $IFACE clsact
sudo tc qdisc add dev $IFACE clsact

# See queue_mapping in https://man7.org/linux/man-pages/man8/tc-skbedit.8.html
echo "Removing existing TC filters ..."
filter_count=$(tc filter show dev $IFACE egress | wc -l)
[[ filter_count -gt 0 ]] && sudo tc filter del dev $IFACE egress
echo "Adding skbedit rules for explicit TX queue mapping ..."
filter_added=1
for i in {1..32}; do
    sudo tc filter add dev $IFACE egress protocol ip u32 ht 800: order $filter_added \
                    match ip dst $network_prefix.$ip_octet3_dst.$(echo "100 + $i" | bc) \
                    action skbedit queue_mapping $i
    filter_added=$((filter_added + 1))
done

# This is need to for the above egress queue assignment to preserve and not overwritten by XPS.
echo "Disabling XPS ..."
tmpdir=$(mktemp -d)
cp ./xps_setup.sh $tmpdir/
sudo bash $tmpdir/xps_setup.sh --dev $IFACE --default --disable
rm -r $tmpdir