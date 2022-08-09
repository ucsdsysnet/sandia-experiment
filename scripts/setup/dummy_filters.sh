#!/bin/bash

. scripts/setup/ip_interface.config

NIC_TYPE=$nic_type
NUMBER_DUMMY_FILTERS=$number_dummy_filters

for arg in "$@"
do
case $arg in
    -n|--nictype)
        shift
        NIC_TYPE=$1
        shift
        ;;
    -f|--dummyfilters)
        shift
        NUMBER_DUMMY_FILTERS=$1
        shift
        ;;
esac
done

cd "$(dirname "$0")"

#All dummy filters will be mapped to queue 64; This assumes that there are already 32 legitimate filters;
create_dummy_filters()
{
    echo "Adding skbedit rules for explicit TX queue mapping ..."
    filter_added=33
    number_iterations=$((($number_dummy_filters + 255/2) / 255))
    number_iterations=$((number_iterations - 1))
    for m in {0..255}; do
        for i in $( seq 0 $number_iterations )
        do
            sudo tc filter add dev $3 egress protocol ip u32 ht 800: order $filter_added \
                            match ip dst $1.$2.$m.$i \
                            action skbedit queue_mapping 64
            # echo $m $i
            filter_added=$((filter_added + 1))
            # echo $filter_added
        done
    done

    echo $filter_added

    # This is need to for the above egress queue assignment to preserve and not overwritten by XPS.
    echo "Disabling XPS ..."
    tmpdir=$(mktemp -d)
    cp ./xps_setup.sh $tmpdir/
    sudo bash $tmpdir/xps_setup.sh --dev $3 --default --disable
    rm -r $tmpdir
}

main()
{
    echo $NIC_TYPE
    if [[ $NIC_TYPE = "fpga" ]]; then
        echo "fpga"
        IFS='.' read ip1 ip2 ip3 ip4 <<< "$dummy_ip"
        create_dummy_filters $ip1 $ip2 $FPGA_IFACE 
    else
        IFS='.' read ip1 ip2 ip3 ip4 <<< "$dummy_ip"
        create_dummy_filters $ip1 $ip2 $cx5_IFACE
    fi
}

main
