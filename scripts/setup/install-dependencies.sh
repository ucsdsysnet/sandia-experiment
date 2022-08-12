#!/bin/bash

cwd="$(pwd)"
cd "$(dirname "$0")"

sudo apt-get update 

tempdir=$(mktemp -d)
cd $tempdir

# Install Mellanox OFED

wget https://content.mellanox.com/ofed/MLNX_OFED-5.5-1.0.3.2/MLNX_OFED_LINUX-5.5-1.0.3.2-ubuntu20.04-x86_64.tgz

tar zxf MLNX_OFED_LINUX-5.5-1.0.3.2-ubuntu20.04-x86_64.tgz
cd MLNX_OFED_LINUX-5.5-1.0.3.2-ubuntu20.04-x86_64

sudo ./mlnxofedinstall --upstream-libs
sudo /etc/init.d/openibd restart

# Install Mellanxo IRQ affinity tools if needed. Modern OFED often includes these tools.
if ! [ -x "`command -v set_irq_affinity_bynode.sh`" ]; then
    wget http://www.mellanox.com/relateddocs/prod_software/mlnx_irq_affinity.tgz
    tar xzf mlnx_irq_affinity.tgz --directory=/usr/sbin/ --overwrite
fi

cd "$cwd"
