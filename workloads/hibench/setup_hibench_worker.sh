#!/bin/bash

. workloads/hibench/configurations.config
MASTER_PUBLIC_IP=$master_public_ip

sudo chown -R $USER $HOME

# sudo apt-get update
# sudo apt-get remove --purge openjdk-11-'*'
# sudo apt-get install -y openjdk-8-jdk

var=$HOME/sw
mkdir -p $var
cd $var

# scp -r $USER@$MASTER_PUBLIC_IP:$HOME/sw/hadoop-3.2.4.tar.gz $HOME/sw