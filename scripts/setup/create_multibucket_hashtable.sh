#!/bin/bash

cd "$(dirname "$0")"

source ../shared.sh
IFACE=$(get_cx5_iface)
ip_octet3_src=10
ip_octet3_dst=20
network_prefix='10.10'
network_prefix_len=16

# sudo tc qdisc del dev $IFACE clsact
# sudo tc qdisc add dev $IFACE clsact

# See queue_mapping in https://man7.org/linux/man-pages/man8/tc-skbedit.8.html
# echo "Removing existing TC filters ..."
# filter_count=$(tc filter show dev $IFACE egress | wc -l)
# [[ filter_count -gt 0 ]] && sudo tc filter del dev $IFACE egress

# #Create root qdisc (class 90 — for unclassified traffic):
# sudo tc qdisc add dev ens4 root handle 1: htb default 90

#Root class:
tc class add dev ens4 parent 1:0 classid 1:1 
sudo tc qdisc add dev ens4 root handle 1: multiq

# #Root filter
# sudo tc filter add dev ens4 parent 1:0 prio 5 protocol ip u32

# #Create a hash table called 2: with 32 buckets
# sudo tc filter add dev ens4 parent 1:0 prio 5 handle 2: protocol ip u32 divisor 32

# #Direct traffic in root filter to hash table 2: we created earlier
# sudo tc filter add dev ens4 parent 1:0 protocol ip prio 5 \
#         u32 ht 800:: \
#         match ip dst 10.10.20.0/24 \
#         hashkey mask 0x000000ff at 16 \
#         link 2:

#Create filters and add them to the each bucket in hash table 2:
for i in {1..32}; do
    # x=$( printf "%x" $i ) ; 
    sudo tc filter add dev $IFACE egress protocol ip u32 ht 2:$[i-1]: \
        match ip dst $network_prefix.$ip_octet3_dst.$(echo "100 + $i" | bc) \
        action skbedit queue_mapping $i
done

# echo "Adding skbedit rules for explicit TX queue mapping ..."
# filter_added=1
# for i in {1..32}; do
#     sudo tc filter add dev $IFACE egress protocol ip u32 ht 800: order $filter_added \
#                     match ip dst $network_prefix.$ip_octet3_dst.$(echo "100 + $i" | bc) \
#                     action skbedit queue_mapping $i
#     filter_added=$((filter_added + 1))
# done

# This is need to for the above egress queue assignment to preserve and not overwritten by XPS.
echo "Disabling XPS ..."
tmpdir=$(mktemp -d)
cp ./xps_setup.sh $tmpdir/
sudo bash $tmpdir/xps_setup.sh --dev $IFACE --default --disable
rm -r $tmpdir

#tc -s qdisc show dev ens4
#tc filter show dev ens4 egress | grep match | wc -l
#tc filter show dev ens4 egress