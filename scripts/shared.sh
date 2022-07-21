#/bin/bash

SENDER_HOSTNAME="yeti-01"

# Select interface: Corundum or ConnectX-5
get_iface()
{
    hostname="$(hostname -s)"
    if [[ "$hostname" == "$SENDER_HOSTNAME" ]]; then
        echo >&2 "$hostname (sender): using ConnectX-5"
        get_corundum_iface
        # get_cx5_iface
    else
        echo >&2 "$hostname (receiver): using ConnectX-5"
        get_corundum_iface
        # get_cx5_iface
    fi
}

get_corundum_iface()
{
    echo "ens2"
}

get_cx5_iface()
{
    echo "$(ibdev2netdev | cut -f5 -d' ')"
    # echo "$(ibdev2netdev | grep 'mlx5' | regex 'mlx5.* port .* ==> (\w+)' 1)"
}
