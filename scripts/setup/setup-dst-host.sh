#!/bin/bash

cd "$(dirname "$0")"

source ../shared.sh
IFACE=$(get_iface)

# (optional) delete existing IPs
ip addr show $IFACE | grep "inet " | awk '{print $2}' | xargs -I {} sudo ip addr del {} dev $IFACE

# Destination host:
for i in {1..32}; do
    sudo ip addr add 10.0.0.$((200 + $i))/32 dev $IFACE
done