#!/bin/zsh

parallelism=1
server=localhost

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

regex () {
    gawk 'match($0,/'$1'/, ary) {print ary['${2:-'0'}']}'
}

source ../shared.sh
IFACE=$(get_iface)

nic_local_numa_node=$(cat /sys/class/net/$IFACE/device/numa_node)

# set -x
output=$(
for i in $(seq 1 $parallelism); do
    port=$(echo "5100+$i" | bc);
    current_server=$server
    if [[ $USE_SEPARATE_SERVER -eq 1 ]]; then
        echo >&2 "Using separate servers ..."
        server_prefix=${server%.*}
        server_suffix=${server##*.}
        current_suffix=$(echo "$server_suffix + $i" | bc)
        current_server="$server_prefix.$current_suffix"
        echo >&2 "\t$i-th server: $current_server"
    fi
    numactl -N $nic_local_numa_node iperf3 -c $current_server -T s$i -p $port &;
done
)

sender_total_tput=$(echo $output | grep "sender" | regex '([0-9.]*) Gbits\/sec' 1 | awk '{sum+=$1} END {print sum}')
receiver_total_tput=$(echo $output | grep "receiver" | regex '([0-9.]*) Gbits\/sec' 1 | awk '{sum+=$1} END {print sum}')

echo "parallel: $parallelism, sender: $sender_total_tput, receiver: $receiver_total_tput"
