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
    --cluster_mode)
        shift
        CLUSTER_MODE=1
        ;;
esac
done

# #CX5
# ./scripts/setup/install-dependencies.sh

# #BOTH
# ./scripts/setup/setup-generic.sh

# #CX5
# ./scripts/setup/setup-cx5.sh

# #FPGA
# ./scripts/setup/network_settings.sh -n fpga

# #CX5
# ./scripts/setup/setup-ip.sh -n cx5 -h dst
# ./scripts/setup/setup-ip.sh -n cx5 -h dst --assign-multiple-ips

# #FPGA
# ./scripts/setup/setup-ip.sh -n fpga -h dst
# ./scripts/setup/setup-ip.sh -n fpga -h dst --assign-multiple-ips

main()
{
    sudo apt-get update 
    sudo apt-get -y install zsh net-tools iperf3 numactl
    ./scripts/setup/setup-generic.sh

    if [[ $NIC_TYPE = "fpga" ]]; then
        ./scripts/setup/network_settings.sh -n fpga 
        if [[ $CLUSTER_MODE -eq 1 ]]; then
            ./scripts/setup/setup-ip.sh -n fpga -h dst --assign-multiple-ips
        else
            ./scripts/setup/setup-ip.sh -n fpga -h dst
        fi
    else
        ./scripts/setup/install-dependencies.sh
        ./scripts/setup/setup-cx5.sh
        if [[ $CLUSTER_MODE -eq 1 ]]; then
            ./scripts/setup/setup-ip.sh -n cx5 -h dst --assign-multiple-ips
        else
            ./scripts/setup/setup-ip.sh -n cx5 -h dst
        fi
    fi
}

main