#!/bin/bash

# sudo chown -R $USER $HOME

# sudo apt-get update
# sudo apt-get remove --purge openjdk-11-'*'
# sudo apt-get install -y openjdk-8-jdk

# sudo apt-get install -y maven
# sudo apt-get install -y scala

# java -version; javac -version; scala -version; git --version

# var=$HOME/sw
# mkdir -p $var
# cd $var

# wget https://dlcdn.apache.org/hadoop/common/hadoop-3.2.4/hadoop-3.2.4.tar.gz
# tar -xzvf hadoop-3.2.4.tar.gz 
# mv hadoop-3.2.4 $HOME/hadoop

# echo 'JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")' >> $HOME/hadoop/etc/hadoop/hadoop-env.sh

$HOME/hadoop/bin/hadoop 

# cd $HOME/sw 
# git clone https://github.com/Intel-bigdata/HiBench.git

# Build Hadoop and spark benchmarks
cd  $HOME/sw/HiBench
mvn -Phadoopbench -Psparkbench -Dspark=2.4 -Dscala=2.11 clean package