#!/bin/bash

. workloads/hibench/configurations.config
KEY_FILE=$key_file

eval `ssh-agent -s`
ssh-add $HOME/.ssh/$KEY_FILE
stop-dfs.sh
stop-yarn.sh