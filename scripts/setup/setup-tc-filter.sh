#/bin/bash

get_iface()
{
    echo "$(ibdev2netdev | cut -f5 -d' ')"
    # echo "$(ibdev2netdev | grep 'mlx5' | regex 'mlx5.* port .* ==> (\w+)' 1)"
}

IFACE=$(get_iface)

# Source host:
sudo tc filter del dev $IFACE
for i in {1..32}; do
    sudo tc filter add dev $IFACE protocol ip parent 1: prio 0 u32 \
                    match ip dst 10.0.0.$(echo "200 + $i" | bc) \
                    action skbedit queue_mapping $i
done

# Destination host:
for i in {1..32}; do
    sudo ip addr add 10.0.0.$((200 + $i))/32 dev $IFACE
done