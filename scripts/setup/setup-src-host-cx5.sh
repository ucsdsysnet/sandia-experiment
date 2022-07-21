#!/bin/bash

cd "$(dirname "$0")"

TOTAL_RULES_GROUPS=1

source ../shared.sh
IFACE=$(get_cx5_iface)
ip_octet3_src=10
ip_octet3_dst=20
network_prefix='10.10'
network_prefix_len=16

for arg in "$@"
do
case $arg in
    --enable-tc-mapping)
        shift
        ENABLE_TC_MAPPING=1
        ;;
    --assign-multiple-ips)
        shift
        ASSING_MULTIPLE_IPS=1
        ;;
esac
done

# Source host:

sudo ip link set $IFACE up
ip addr show $IFACE | grep "inet " | awk '{print $2}' | xargs -I {} sudo ip addr del {} dev $IFACE
[[ $ASSING_MULTIPLE_IPS -eq 1 ]] && MAX_IP=32 || MAX_IP=0
for i in $(seq 0 $MAX_IP); do
    sudo ip addr add $network_prefix.$ip_octet3_src.$((100 + $i))/$network_prefix_len dev $IFACE
done

echo "Reseting qdisc to default ..."
# sudo tc qdisc del dev $IFACE root
sudo tc qdisc del dev $IFACE clsact

# Initially, `multiq` was used in combination with skbedit according to
#   https://www.kernel.org/doc/Documentation/networking/multiqueue.txt
: '
if [[ $ENABLE_TC_MAPPING -eq 1 ]]; then
    echo "Switching to multiq for direct access to hardware queues ..."
    sudo tc qdisc add dev $IFACE root handle 1: multiq
fi
#'

# However, we found the performance to be limited to using a single core,
#   so we switched to `clsact` as suggested here:
#   https://www.spinics.net/lists/netdev/msg365702.html
sudo tc qdisc add dev $IFACE clsact

# See queue_mapping in https://man7.org/linux/man-pages/man8/tc-skbedit.8.html
echo "Removing existing TC filters ..."
filter_count=$(tc filter show dev $IFACE egress | wc -l)
[[ filter_count -gt 0 ]] && sudo tc filter del dev $IFACE egress
if [[ $ENABLE_TC_MAPPING -eq 1 ]]; then
    echo "Adding skbedit rules for explicit TX queue mapping ..."
    filter_added=1
    # for j in $(seq 0 1 $TOTAL_RULES_GROUPS); do
    for i in {1..32}; do
        # sudo tc filter add dev $IFACE protocol ip parent 1: prio 1 u32 \
        #                 match ip dst 10.0.$ip_octet3.$(echo "200 + $i" | bc) \
        #                 action skbedit queue_mapping $i
        # Note: Either of the two ways below works, although matching on src ip requires
        #   iperf3 client binding and multiple IPs on sender side.
        sudo tc filter add dev $IFACE egress protocol ip u32 ht 800: order $filter_added \
                        match ip dst $network_prefix.$ip_octet3_dst.$(echo "100 + $i" | bc) \
                        action skbedit queue_mapping $i
        filter_added=$((filter_added + 1))
    done
    # sudo tc filter add dev $IFACE egress protocol ip u32 ht 800: order $i \
    #                 match ip src 10.0.$ip_octet3.$(echo "100 + $i" | bc) \
    #                 action skbedit queue_mapping $i
    # done
fi

# This is need to for the above egress queue assignment to preserve and not overwritten by XPS.
echo "Disabling XPS ..."
tmpdir=$(mktemp -d)
cp ./xps_setup.sh $tmpdir/
sudo bash $tmpdir/xps_setup.sh --dev $IFACE --default --disable
rm -r $tmpdir