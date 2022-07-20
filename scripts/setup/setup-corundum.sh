#!/bin/zsh

cd "$(dirname "$0")"

. ../shared.sh
IFACE=$(get_corundum_iface)

declare -A HOST2IP=(
    ["yeti-01"]="10.5.11.100"
    ["yeti-04"]="10.5.44.100"
)

# declare -A HOST2MAC=(
#     ["yeti-04"]="00:21:b2:25:1d:c0"
#     ["yeti-01"]="d0:94:66:48:a0:b1"
# )

MY_HOST=$(hostname -s)
MTU=1500

set_ip()
{
    MY_IP=${HOST2IP[$MY_HOST]}
    if [ -z "$MY_IP" ]; then
        echo >&2 "Host not found in IP mapping"
        return 1
    fi

    # delete existing IPs
    ip addr show $IFACE | grep "inet " | awk '{print $2}' | xargs -I {} sudo ip addr del {} dev $IFACE

    sudo ip addr add $MY_IP/32 dev $IFACE
    ACTUAL_IP=$(ip addr show $IFACE | grep "inet " | awk '{print $2}')
    if [ "$MY_IP/32" != "$ACTUAL_IP" ]; then
        echo >&2 "Failed to set IP to $MY_IP. Got $ACTUAL_IP instead."
        return 1
    fi
}

main()
{
    # sudo ip link set $IFACE up
    # set_ip
    sudo ip link set $IFACE mtu $MTU
    sudo ethtool -K $IFACE gso on
}

main