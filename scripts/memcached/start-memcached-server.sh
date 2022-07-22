
#!/bin/bash

cd "$(dirname "$0")"

parallelism=1

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

# source ../shared.sh
# IFACE=$(get_iface)
# IFACE=ens1f0
# nic_local_numa_node=$(cat /sys/class/net/$IFACE/device/numa_node)

server_port_pair=''
if [[ $USE_SEPARATE_SERVER != 1 ]]; then
    server_port_pair="$server:11211"
fi

if [[ $USE_SEPARATE_SERVER -eq 1 ]]; then
    for i in $(seq 1 $parallelism);
    do
        port=$(echo "11211+$i" | bc)
        current_server=$server
        # echo >&2 "Using separate servers ..."
        IFS='.' read ip1 ip2 ip3 ip4 <<< "$server"
        # ip2=$(echo "1 + ($i - 1) / 32" | bc)
        ip4=$(echo "$ip4 + ($i - 1) % 32 + 1" | bc)
        current_server="$ip1.$ip2.$ip3.$ip4"
        # echo >&2 "\t$i-th server: $current_server"
        server_port_pair+="$current_server:$port,"
        
    done
fi

echo $server_port_pair
memcached -l $server_port_pair &

#Check your new settings with ss to confirm the change:
output=$(sudo ss -plunt | grep memcached)
echo $output

# memcached -l 10.1.2.231:11211,10.1.2.232:11212

#./scripts/memcached/start-multiple-memcached-instances.sh -p 32 -s 10.1.2.200 --separate-servers

