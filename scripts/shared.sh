#/bin/bash

# Get interface name for Mellanox CX-5
get_iface()
{
    echo "$(ibdev2netdev | cut -f5 -d' ')"
    # echo "$(ibdev2netdev | grep 'mlx5' | regex 'mlx5.* port .* ==> (\w+)' 1)"
}
