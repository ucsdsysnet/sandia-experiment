#!/bin/bash

. workloads/hibench/configurations.config
WORKER_NODES=$worker_nodes
KEY_FILE=$key_file
MASTER_PORT=$hibench_port
MASTER_LOCAL_IP=$master_local_ip

# Duplicate Config Files on Each Worker Node
IFS=',' read -ra WORKER <<< "$WORKER_NODES"
for i in "${WORKER[@]}"; do
        eval `ssh-agent -s`
        ssh-add $HOME/.ssh/$KEY_FILE
        scp -r $HOME/hadoop/etc/hadoop/* $USER@$i:$HOME/hadoop/etc/hadoop/
done

sudo apt install python2
cp $HOME/sw/HiBench/conf/hadoop.conf.template $HOME/sw/HiBench/conf/hadoop.conf
sed -i "s|/PATH/TO/YOUR/HADOOP/ROOT|$HOME\/hadoop|g" $HOME/sw/HiBench/conf/hadoop.conf
sed -i "s|localhost:8020|$MASTER_LOCAL_IP:$MASTER_PORT|g" $HOME/sw/HiBench/conf/hadoop.conf
