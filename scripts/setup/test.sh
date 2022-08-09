#!/bin/bash

# cd "$(dirname "$0")"

# for i in {36..1060}; do
#     test=$(echo $i%256 | bc)
#     echo $test
# done

. scripts/setup/ip_interface.config

echo "$cx5_IFACE" "$cx5_sender_ip"