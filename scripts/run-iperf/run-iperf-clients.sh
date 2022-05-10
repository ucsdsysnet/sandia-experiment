#!/bin/zsh

cd "$(dirname "$0")"

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
IFACE_CX5=$(get_cx5_iface)
[[ "$IFACE" == "$IFACE_CX5" ]] && ip_octet3=1 || ip_octet3=2

nic_local_numa_node=$(cat /sys/class/net/$IFACE/device/numa_node)

# set -x
output=$(
for i in $(seq 1 $parallelism); do
    port=$(echo "5100+$i" | bc);
    bind_src_ip_last_octet=100
    bind_src_ip="10.0.$ip_octet3.$bind_src_ip_last_octet"
    current_server=$server
    if [[ $USE_SEPARATE_SERVER -eq 1 ]]; then
        echo >&2 "Using separate servers ..."
        server_prefix=${server%.*}
        server_suffix=${server##*.}
        current_suffix=$(echo "$server_suffix + $i" | bc)
        current_server="$server_prefix.$current_suffix"
        bind_src_ip_last_octet=$(echo "100 + $i" | bc)
        bind_src_ip="10.0.$ip_octet3.$bind_src_ip_last_octet"
        echo >&2 "\t$i-th server: $current_server"
    fi
    bind_src_ip="10.0.$ip_octet3.$bind_src_ip_last_octet"
    # Note: -B $bind_src_ip is needed if using match on src ip.
    #   Also enable assign-multiple-ips in setup-src.host.sh script.
    numactl -N $nic_local_numa_node iperf3 -c $current_server -T s$i -p $port &;
done
)

# set -x
sender_total_tput=$(echo $output | grep "sender" | regex '([0-9.]*) Gbits\/sec' 1 | awk '{sum+=$1} END {print sum}')
sender_total_tput_mbps=$(echo $output | grep "sender" | regex '([0-9.]*) Mbits\/sec' 1 | awk '{sum+=$1} END {print sum}')
sender_total_tput=$(echo "scale=3; ${sender_total_tput:-0} + ${sender_total_tput_mbps:-0}/1000" | bc -l)
receiver_total_tput=$(echo $output | grep "receiver" | regex '([0-9.]*) Gbits\/sec' 1 | awk '{sum+=$1} END {print sum}')
receiver_total_tput_mbps=$(echo $output | grep "receiver" | regex '([0-9.]*) Mbits\/sec' 1 | awk '{sum+=$1} END {print sum}')
receiver_total_tput=$(echo "scale=3; ${receiver_total_tput:-0} + ${receiver_total_tput_mbps:-0}/1000" | bc -l)

echo "parallel: $parallelism, sender: $sender_total_tput, receiver: $receiver_total_tput"
