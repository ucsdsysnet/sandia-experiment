#!/bin/bash

cd "$(dirname "$0")"

source ../shared.sh
IFACE=$(get_corundum_iface)
ip_octet3_src=10
ip_octet3_dst=20
network_prefix='10.25'
network_prefix_len=16

echo "Adding skbedit rules for explicit TX queue mapping ..."
filter_added=36
for i in {36..1060}; do
    sudo tc filter add dev $IFACE egress protocol ip u32 ht 800: order $filter_added \
                    match ip dst $network_prefix.$(echo $i%256 | bc).$(echo $i%256 | bc) \
                    action skbedit queue_mapping $i
    filter_added=$((filter_added + 1))
    echo $filter_added
done

# This is need to for the above egress queue assignment to preserve and not overwritten by XPS.
echo "Disabling XPS ..."
tmpdir=$(mktemp -d)
cp ./xps_setup.sh $tmpdir/
sudo bash $tmpdir/xps_setup.sh --dev $IFACE --default --disable
rm -r $tmpdir