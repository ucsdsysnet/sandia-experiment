## Setup Hadoop bench in HiBench (On Master Node - Control node in this test suite)
```
./workloads/hibench/setup_hibench.sh
```

## Setup worker nodes (Run on each worker node)
```
./workloads/hibench/setup_hibench_worker.sh
```

## Configure HiBench (Run on master)
```
./workloads/hibench/configure_hibench.sh
```

## Make sure /etc/hosts is correct on all nodes

## Start and Stop HiBench
```
./workloads/hibench/start_hibench.sh 
./workloads/hibench/stop_hibench.sh 
```

## Verification - After you start HiBench run 'jps' command

### On master you should see the following
```
519349 SecondaryNameNode
520148 NodeManager
519780 ResourceManager
518800 NameNode
519020 DataNode
520554 Jps
```

### On worker you should see the following
```
495413 NodeManager
495696 Jps
495241 DataNode
```

## Testing
```
$HOME/sw/HiBench/bin/workloads/micro/wordcount/prepare/prepare.sh
$HOME/sw/HiBench/bin/workloads/micro/wordcount/hadoop/run.sh

$HOME/sw/HiBench/bin/workloads/micro/terasort/prepare/prepare.sh
$HOME/sw/HiBench/bin/workloads/micro/terasort/hadoop/run.sh

$HOME/sw/HiBench/bin/workloads/micro/sort/prepare/prepare.sh
$HOME/sw/HiBench/bin/workloads/micro/sort/hadoop/run.sh

$HOME/sw/HiBench/bin/run_all.sh

cat $HOME/sw/HiBench/report/hibench.report
```

