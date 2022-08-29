#!/bin/bash

. workloads/hibench/configurations.config
WORKER_NODES=$worker_nodes
KEY_FILE=$key_file

# Duplicate Config Files on Each Worker Node
IFS=',' read -ra WORKER <<< "$WORKER_NODES"
for i in "${WORKER[@]}"; do
        eval `ssh-agent -s`
        ssh-add $HOME/.ssh/$KEY_FILE
        scp -r $HOME/hadoop/etc/hadoop/* $USER@$i:$HOME/hadoop/etc/hadoop/
done
