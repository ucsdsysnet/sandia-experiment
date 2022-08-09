#!/bin/bash

# cd "$(dirname "$0")"

# for i in {36..1060}; do
#     test=$(echo $i%256 | bc)
#     echo $test
# done

. scripts/setup/ip_interface.config

# echo "$cx5_IFACE" "$cx5_sender_ip"

# IFS='.' read ip1 ip2 ip3 ip4 <<< "$cx5_src_ip"
# test=$ip1.$ip2.$ip3.$(($ip4 + $ip1))
# echo $test

# echo $((($1 + $2/2) / $2))
number_iterations=$((($number_dummy_filters + 255/2) / 255))
echo $number_iterations