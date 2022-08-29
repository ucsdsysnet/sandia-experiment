#!/bin/bash

. workloads/hibench/configurations.config

MASTER_HOSTNAME=$master_hostname
MASTER_PUBLIC_IP=$master_public_ip
WORKER_NODES=$worker_nodes

sudo chown -R $USER $HOME

sudo apt-get update
sudo apt-get remove --purge openjdk-11-'*'
sudo apt-get install -y openjdk-8-jdk

sudo apt-get install -y maven
sudo apt-get install -y scala

java -version; javac -version; scala -version; git --version

var=$HOME/sw
mkdir -p $var
cd $var

wget https://dlcdn.apache.org/hadoop/common/hadoop-3.2.4/hadoop-3.2.4.tar.gz
tar -xzvf hadoop-3.2.4.tar.gz 
mv hadoop-3.2.4 $HOME/hadoop

echo 'JAVA_HOME=$(readlink -f /usr/bin/java | sed "s:bin/java::")' >> $HOME/hadoop/etc/hadoop/hadoop-env.sh

$HOME/hadoop/bin/hadoop 

cd $HOME/sw 
git clone https://github.com/Intel-bigdata/HiBench.git

Build Hadoop and spark benchmarks
cd  $HOME/sw/HiBench
mvn -Phadoopbench -Psparkbench -Dspark=2.4 -Dscala=2.11 clean package

echo 'PATH=$HOME/hadoop/bin:$HOME/hadoop/sbin:$PATH' >> $HOME/.profile
echo 'export HADOOP_HOME=$HOME/hadoop' >> $HOME/.bashrc
echo 'export PATH=${PATH}:${HADOOP_HOME}/bin:${HADOOP_HOME}/sbin' >> $HOME/.bashrc

sed -i '/\<configuration\>/d' $HOME/hadoop/etc/hadoop/core-site.xml
sed -i '/\<\/configuration\>/d' $HOME/hadoop/etc/hadoop/core-site.xml

echo """<configuration>
        <property>
            <name>fs.default.name</name>
            <value>hdfs://$MASTER_HOSTNAME:9000</value>
        </property>
    </configuration>""" >> $HOME/hadoop/etc/hadoop/core-site.xml

sed -i '/\<configuration\>/d' $HOME/hadoop/etc/hadoop/hdfs-site.xml
sed -i '/\<\/configuration\>/d' $HOME/hadoop/etc/hadoop/hdfs-site.xml

echo """<configuration>
    <property>
            <name>dfs.namenode.name.dir</name>
            <value>$HOME/data/nameNode</value>
    </property>

    <property>
            <name>dfs.datanode.data.dir</name>
            <value>$HOME/data/dataNode</value>
    </property>

    <property>
            <name>dfs.replication</name>
            <value>1</value>
    </property>
</configuration>""" >> $HOME/hadoop/etc/hadoop/hdfs-site.xml

# Set YARN as Job Scheduler
sed -i '/\<configuration\>/d' $HOME/hadoop/etc/hadoop/mapred-site.xml
sed -i '/\<\/configuration\>/d' $HOME/hadoop/etc/hadoop/mapred-site.xml

echo """<configuration>
    <property>
            <name>mapreduce.framework.name</name>
            <value>yarn</value>
    </property>
    <property>
            <name>yarn.app.mapreduce.am.env</name>
            <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
    </property>
    <property>
            <name>mapreduce.map.env</name>
            <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
    </property>
    <property>
            <name>mapreduce.reduce.env</name>
            <value>HADOOP_MAPRED_HOME=$HADOOP_HOME</value>
    </property>
</configuration>""" >> $HOME/hadoop/etc/hadoop/mapred-site.xml

# Configure YARN
sed -i '/\<configuration\>/d' $HOME/hadoop/etc/hadoop/yarn-site.xml
sed -i '/\<\/configuration\>/d' $HOME/hadoop/etc/hadoop/yarn-site.xml

echo """<configuration>
    <property>
            <name>yarn.acl.enable</name>
            <value>0</value>
    </property>

    <property>
            <name>yarn.resourcemanager.hostname</name>
            <value>$MASTER_PUBLIC_IP</value>
    </property>

    <property>
            <name>yarn.nodemanager.aux-services</name>
            <value>mapreduce_shuffle</value>
    </property>
</configuration>""" >> $HOME/hadoop/etc/hadoop/yarn-site.xml

IFS=',' read -ra WORKER <<< "$WORKER_NODES"
for i in "${WORKER[@]}"; do
    echo "$i" >> $HOME/hadoop/etc/hadoop/workers
done

# Run this command everytime you change any xml files 
hdfs namenode -format