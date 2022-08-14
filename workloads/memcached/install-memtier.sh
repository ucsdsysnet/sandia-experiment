#!/bin/bash

sudo apt-get install build-essential autoconf automake libpcre3-dev libevent-dev pkg-config zlib1g-dev libssl-dev

# sudo chown -R $USER /opt
cd ..
echo $(pwd)
git clone https://github.com/RedisLabs/memtier_benchmark.git
cd memtier_benchmark
echo $(pwd)
autoreconf -ivf
./configure
make
sudo make install

#memtier_benchmark --help

#populate memcached with items (only write requests)
#memtier_benchmark -s 192.168.1.2 -p 11211 -P memcache_text --show-config --ratio=1:0 --requests 20000

#only read requests
#memtier_benchmark -s 192.168.1.2 -p 11211 -P memcache_text --show-config --ratio=0:1

#STAT curr_items 19976 (Current number of items stored)
#STAT total_items 2000000 (Total number of items stored since the server started)
# Object data size (default: 32)
#Key size: 9~16Bytes 