##### Install memcached server
```
./scripts/memcached/install-memcached-server.sh 
```

#### Install memtier benchmark tool (On both client and server)
```
./scripts/memcached/install-memtier.sh
```

##### Start memcached server
```
./scripts/memcached/start-memcached-server.sh -s 10.10.20.100 -p 32 --separate-servers
```

##### Populate memcached server with data 
```
./scripts/memcached/populate-memcached-with-data.sh -s 10.10.20.101 -p 11212
```

#### Run memtier benachmark tool
```
./scripts/memcached/run-memtier-benchmark.sh -s 10.10.20.100 -p 32 --separate-servers
```

#### Kill memcached instances
```
./scripts/memcached/kill-memcached.sh
```

### Memcached server -> view stats
```
telnet 10.10.20.101 11212
stats items
stats detail
stats sizes
stats reset
stats slabs
stats malloc

stats cachedump 2 200

quit
```