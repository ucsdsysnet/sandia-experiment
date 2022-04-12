#/bin/bash

# Get interface name for Mellanox CX-5
get_iface()
{
    # get_corundum_iface
    get_cx5_iface
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
