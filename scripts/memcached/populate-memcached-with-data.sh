#!/bin/bash

server=127.0.0.1
port=11211

for arg in "$@"
do
case $arg in
    -s|--server)
        shift
        server=$1
        shift
        ;;
    -p|--port)
        shift
        port=$1
        shift
        ;;
esac
done

echo $server
echo $port

# memtier_benchmark -s 10.1.2.201 -p 11212 -P memcache_text --show-config --ratio=1:0 --requests 20000

#RAM SIZE 127GB available 121GB; machine has 48 threads (24 cores; 2 threads per core)

#default
#populate 19976 items; Data size:32 bytes; Key Size:9-16 bytes; memcached protocol - text; Key pattern:random
#number of threads:4; number of clients per thread:50; number of requests per client:20000;
# memtier_benchmark -s $server -p $port -P memcache_text --show-config --ratio=1:0 --requests 200000

# ./scripts/memcached/populate-memcached-with-data.sh -s 10.1.2.201 -p 11212

#with one request from each 50 clients with 4 threads stats output is as follows;
# memtier_benchmark -s $server -p $port -P memcache_text --show-config --ratio=1:0 -t 4 --requests 1
# 4 * 50 * 1 = 200
# STAT bytes 106
# STAT curr_items 1
# STAT total_items 200

# stats cachedump 2 200 shows only 1 item as follows
# ITEM memtier-6263819 [32 b; 0 s]

#store 559232 items with 2000000 requests
#store 559232 items with 3000000 requests
#Therefore if you just want to prepopulate data, just increasing the request count(number of items you want to store) with just one thread with one client would do as follows
memtier_benchmark -s $server -p $port -P memcache_text --show-config --ratio=1:0 -t 4 -c 10 --requests 1000000
# memtier_benchmark -s 10.1.2.202 -p 11213 -P memcache_text --show-config --ratio=1:0 --key-maximum 20000000 --key-pattern=R:R -t 1 -c 1 --requests 10