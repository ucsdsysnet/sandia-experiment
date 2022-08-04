#!/bin/bash

cd "$(dirname "$0")"

source ../shared.sh
IFACE=$(get_cx5_iface)
ip_octet3_src=10
ip_octet3_dst=20
network_prefix='10.10'
network_prefix_len=16

# sudo tc qdisc del dev ens4 clsact
# sudo tc qdisc add dev ens4 clsact
# Qdisc "clsact" is classless.

# See queue_mapping in https://man7.org/linux/man-pages/man8/tc-skbedit.8.html
# echo "Removing existing TC filters ..."
# filter_count=$(tc filter show dev $IFACE egress | wc -l)
# [[ filter_count -gt 0 ]] && sudo tc filter del dev $IFACE egress

#create a hashtable with 32 buckets in egress path
sudo tc filter add dev ens4 egress prio 1 handle 2: protocol ip u32 divisor 64

# for i in {1..32}; do
#     x=$( printf "%x" $i ) ; 
#     sudo tc filter add dev $IFACE egress u32 \
#         ht 2: sample u32 0x00000800 0x000000ff at 16 \
#         # hashkey mask 0x000000ff at 16 \
#         match ip dst $network_prefix.$ip_octet3_dst.$(echo "100 + $i" | bc) \
#         action skbedit queue_mapping $i
# done

# tc filter add dev eth0 parent 1: prio 99 u32 \
#                       ht 1: sample u32 0x00000800 0x0000ff00 at 12 \
#                       match ip src 192.168.8.0/24 classid 1:1

# Direct traffic in root hashtable 800: to hash table 2: we created earlier
# sudo tc filter add dev ens4 egress protocol ip prio 1 \
#         u32 ht 800:: \
#         match ip dst 10.10.20.0/24 \
#         link 2:

#Create filters and add them to the each bucket in hash table 2:
for i in {1..32}; do
    # x=$( printf "%x" $i ) ; 
    sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 2:$[i-1]: \
                      match ip dst 10.10.20.$(echo "100 + $i" | bc) \
                      action skbedit queue_mapping $i
done

# for i in {1..32}; do
#     # x=$( printf "%x" $i ) ; 
#     sudo tc filter add dev $IFACE egress protocol ip u32 ht 2:$[i-1]: \
#         hashkey mask 0x000000ff at 16 \
#         match ip dst $network_prefix.$ip_octet3_dst.$(echo "100 + $i" | bc) \
#         action skbedit queue_mapping $i
# done

# sudo tc filter add dev ens4 egress prio 1 u32 \
#                     link 2: hashkey mask 0x000000ff at 16 \
#                     match ip dst 10.10.20.0/24 \
#                     action skbedit queue_mapping 1

            

# This is need to for the above egress queue assignment to preserve and not overwritten by XPS.
echo "Disabling XPS ..."
tmpdir=$(mktemp -d)
cp ./xps_setup.sh $tmpdir/
sudo bash $tmpdir/xps_setup.sh --dev $IFACE --default --disable
rm -r $tmpdir

#################################################################################################
#tc -s qdisc show dev ens4
#tc filter show dev ens4 egress | grep match | wc -l
#tc filter show dev ens4 egress
#sudo tc filter del dev ens4 egress


#sudo tc qdisc add dev eth2 root handle 1: mq
#sudo tc filter add dev ens4 egress parent ffff: prio 5 handle 2: protocol ip u32 divisor 32

# sudo tc filter add dev ens4 egress protocol ip u32 ht 800: \
#     match ip dst 192.168.0.3 \
# 	action skbedit queue_mapping 3

# #Create root qdisc (class 90 — for unclassified traffic):
# sudo tc qdisc add dev ens4 root handle 1: htb default 90

#Root class:
# tc class add dev ens4 parent 1:0 classid 1:1 
# sudo tc qdisc add dev ens4 root handle 1: multiq

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

#################################################################################################