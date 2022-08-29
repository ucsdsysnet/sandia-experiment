#!/bin/bash

sudo chown -R $USER $HOME

sudo apt-get update
sudo apt-get remove --purge openjdk-11-'*'
sudo apt-get install -y openjdk-8-jdk

var=$HOME/sw
mkdir -p $var
cd $var

mv $HOME/hadoop-3.2.4.tar.gz $HOME/sw
cd $HOME/sw
tar -xvf hadoop-3.2.4.tar.gz
mv hadoop-3.2.4 hadoop


