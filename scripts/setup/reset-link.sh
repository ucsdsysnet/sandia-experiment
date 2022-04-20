#!/bin/bash

cd "$(dirname "$0")"

source ../shared.sh
IFACE=$(get_iface)
IFACE_CX5=$(get_cx5_iface)
[[ "$IFACE" == "$IFACE_CX5" ]] && sudo /etc/init.d/openibd restart

sudo ip addr flush $IFACE
sudo ip link set $IFACE down
sudo ip link set $IFACE up
