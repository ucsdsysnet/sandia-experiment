#!/bin/bash

cwd="$(pwd)"
cd "$(dirname "$0")"

sudo apt update
sudo apt install memcached
sudo apt install libmemcached-tools

IFACE=ens1f0
local_ip=$(ifconfig | grep -A1 $IFACE | grep inet | awk '{{print $2}}')

# echo $local_ip
#cat /etc/memcached.conf

#Change the ip to use the local private network
sudo sed -i -e "s/\(-l\).*/\1 $local_ip/" /etc/memcached.conf
