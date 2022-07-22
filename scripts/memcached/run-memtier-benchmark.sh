#!/bin/bash

#Only read requests
#memtier_benchmark -s 192.168.1.2 -p 11211 -P memcache_text --show-config --ratio=0:1
# ./scripts/memcached/run-memtier-benchmark.sh -s 10.10.20.100 -p 2 --separate-servers

parallelism=1
server=127.0.0.1

mkdir -p /tmp/data-tmp
tmp_folder='/tmp/data-tmp'
timestamp=$(date +%d-%m-%Y_%H-%M-%S)

threads=1
clients_per_thread=20
requests_per_client=10000
TAR_FILENAME="memt-t$threads-c$clients_per_thread-r$requests_per_client-$timestamp.tar"

for arg in "$@"
do
case $arg in
    -p|--parallel)
        shift
        parallelism=$1
        shift
        ;;
    -s|--server)
        shift
        server=$1
        shift
        ;;
    --separate-servers)
        shift
        USE_SEPARATE_SERVER=1
        ;;
esac
done

if [[ $USE_SEPARATE_SERVER != 1 ]]; then
    logname="memt-log.json"
    echo "hello"
    memtier_benchmark -s $server -p 11211 -P memcache_text --ratio=0:1 -t 1 -c 30 -n 10000 --json-out-file=$logname &
fi

if [[ $USE_SEPARATE_SERVER -eq 1 ]]; then
    for i in $(seq 1 $parallelism); do
        port=$(echo "11211+$i" | bc);
        current_server=$server
        
        # echo >&2 "Using separate servers ..."
        IFS='.' read ip1 ip2 ip3 ip4 <<< "$server"
        ip4=$(echo "$ip4 + ($i - 1) % 32 + 1" | bc)
        current_server="$ip1.$ip2.$ip3.$ip4"
        logname="$tmp_folder/memt-$ip4-$timestamp.json"
        out_file="$tmp_folder/memt-$ip4-$timestamp.txt"
        hdrprefix="$tmp_folder/memt-$ip4-$timestamp"
        echo >&2 "\t$i-th server: $current_server  port: $port"
        
        memtier_benchmark -s $current_server -p $port -P memcache_text --ratio=0:1 -t $threads -c $clients_per_thread -n $requests_per_client -o $out_file --json-out-file=$logname --hdr-file-prefix=$hdrprefix &
    done
fi


cd /tmp/data-tmp && tar -czf $TAR_FILENAME $(cd /tmp/data-tmp && ls | grep $timestamp 2> /dev/null)
# rm -f /tmp/data-tmp/*$timestamp* !(TAR_FILENAME)
find . -type f ! -name "*$timestamp.tar" -exec rm -rf {} \; 