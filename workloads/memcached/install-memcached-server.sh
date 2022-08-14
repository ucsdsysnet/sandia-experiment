#!/bin/bash

cwd="$(pwd)"
cd "$(dirname "$0")"

sudo apt update
sudo apt install memcached
sudo apt install libmemcached-tools

# source ../shared.sh
# IFACE_FPGA=$(get_corundum_iface)
# IFACE_CX5=$(get_cx5_iface)

# local_ip_fpga=$(ifconfig | grep -A1 $IFACE_FPGA | grep inet | awk '{{print $2}}')
# local_ip_cx5=$(ifconfig | grep -A1 $IFACE_CX5 | grep inet | awk '{{print $2}}')

#Change the ip to use the local private network
# sudo sed -i -e "s/\(-l\).*/\1 $local_ip_cx5/" /etc/memcached.conf
# sudo sed -i -e "/$local_ip_cx5$/a -l $local_ip_fpga" /etc/memcached.conf


