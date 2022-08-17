##### Install memcached server (On server)
```
./workloads/memcached/install-memcached-server.sh 
```

#### Install memtier benchmark tool (On client)
```
./workloads/memcached/install-memtier.sh
```

##### Start memcached server (On server)

- Normal Mode (Same IP but different ports)
```
./workloads/memcached/start-memcached-server.sh -s 10.10.20.100 -p 32
```
- Cluster Mode (Different IPs along with different ports)
```
./workloads/memcached/start-memcached-server.sh -s 10.10.20.100 -p 32 --separate-servers
```

##### Populate memcached server with data (On client)
```
./workloads/memcached/populate-memcached-with-data.sh -s 10.10.20.100 -p 11212
```

#### Run memtier benachmark tool (On client)
```
./workloads/memcached/run-memtier-benchmark.sh -s 10.10.20.100 -p 32 --separate-servers
```

#### Kill memcached instances
```
./workloads/memcached/kill-memcached.sh
```

### Memcached server -> view stats
```
telnet 10.10.20.100 11212
stats items
stats detail
stats sizes
stats reset
stats slabs
stats malloc

stats cachedump 2 200

quit
```