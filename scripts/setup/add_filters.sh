#!/bin/bash

. scripts/setup/ip_interface.config

NIC_TYPE=$nic_type

for arg in "$@"
do
case $arg in
    -n|--nictype)
        shift
        NIC_TYPE=$1
        shift
        ;;
esac
done

cd "$(dirname "$0")"

create_filters()
{
    sudo tc qdisc add dev $5 clsact

    # See queue_mapping in https://man7.org/linux/man-pages/man8/tc-skbedit.8.html
    echo "Removing existing TC filters ..."
    filter_count=$(tc filter show dev $5 egress | wc -l)
    [[ filter_count -gt 0 ]] && sudo tc filter del dev $5 egress
    echo "Adding skbedit rules for explicit TX queue mapping ..."
    filter_added=1
    for i in {1..32}; do
        sudo tc filter add dev $5 egress protocol ip u32 ht 800: order $filter_added \
                        match ip dst $1.$2.$3.$(($4 + $i)) \
                        action skbedit queue_mapping $i
        filter_added=$((filter_added + 1))
    done

    # This is need to for the above egress queue assignment to preserve and not overwritten by XPS.
    echo "Disabling XPS ..."
    tmpdir=$(mktemp -d)
    cp ./xps_setup.sh $tmpdir/
    sudo bash $tmpdir/xps_setup.sh --dev $5 --default --disable
    rm -r $tmpdir
}

main()
{
    echo $NIC_TYPE
    if [[ $NIC_TYPE = "fpga" ]]; then
        echo "fpga"
        IFS='.' read ip1 ip2 ip3 ip4 <<< "$FPGA_dst_ip"
        create_filters $ip1 $ip2 $ip3 $ip4 $FPGA_IFACE 
    else
        IFS='.' read ip1 ip2 ip3 ip4 <<< "$cx5_dst_ip"
        create_filters $ip1 $ip2 $ip3 $ip4 $cx5_IFACE
    fi
}

main