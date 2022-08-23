# Setup

#### Change cx5_IFACE and FPGA_IFACE properties with correct interface names in sandia-experiment/scripts/setup/ip_interface.config file

#### Only for CX5 run this - (on both sender and receiver) 
- ./scripts/setup/install-dependencies.sh

#### Setting up CX5 with filters and cluster mode - (on sender)
- ./scripts/setup/sender_setup.sh -n cx5 --add_filters --cluster_mode

#### Setting up CX5 with cluster mode - (on receiver)
- ./scripts/setup/receiver_setup.sh -n cx5 --cluster_mode

#### Setting up FPGA with filters and cluster mode - (on sender)
- ./scripts/setup/sender_setup.sh -n fpga --add_filters --cluster_mode

#### Setting up FPGA with cluster mode - (on receiver)
- ./scripts/setup/receiver_setup.sh -n fpga --cluster_mode

#### If you want to add dummy filters for FPGA for performance enhancement. This will add 2000 dummy rules. (On sender)
- ./scripts/setup/dummy_filters.sh -n fpga

# Run experiments

### Describe your experiements in a json file (sandia-experiment/workloads/template.json) and run 
- python3 workloads/run_experiments.py template.json

- There are three modes
    - CLUSTER
    - NORMAL
    - IP

- Cluster mode behaviour 
    - One to one mapping between clients and servers
    - Number of clients and servers will be based on "parallel" property. "clients" and "server_instances" properties are ignored.
    - Virtual IPs will be taken into account. Virtual IPs are calculated based on the first IP address provided in "server_list" and "client_list". This assumes that the NIC is configured with multiple IPs. 

- Normal mode bahaviour
    - IP list is ignored. 
    - Servers and clients are distinguied only by the ports and will have the same IP (first IP) specified in "server_list" and "client_list".
    - If there are more clients than server instances, clients will pick servers in a round robin manner
    - If there are more servers than clients then there will be idle servers

- Other requirements
    - Control node should have access to all clients and servers. 
    - Control node can behave as one of the clients. 

### Workloads
- NOTE: Memcached experiments assume that the memcached server is up and populated with data. Instrcutions on setting up memcached can be find in sandia-experiment/workloads/memcached/instrcutions.md file. 

# Experiment Analyzer
<!-- - Generic
    - python3 analysis/analyzer.py "file_pattern" "tar_location" "process_location"
        - eg:python3 analysis/analyzer.py "Exp0-r0--iperf-20220818T143252" "/tmp/data-raw" "/tmp/data-processed" -->
- Generic Analyzer (Use this as the base analysis script when developing specific analyzers)
    - analysis/analyzer.py 

- Iperf throughput
    - python3 analysis/iperf_stats.py "file_pattern" "tar_location" "process_location"
        - eg: python3 analysis/iperf_stats.py "Exp0-r0--iperf-20220818T143252" "/tmp/data-raw" "/tmp/data-processed"

# Other Scripts
#### [Only when you need individual scripts instead of going with the default cluster setup]

#### Regardless of the NIC type - Generic performance tuning (On both sender and receiver)
- ./scripts/setup/setup-generic.sh

#### Change network settings (only for FPGA) on both sender and receiver
- ./scripts/setup/network_settings.sh -n fpga

### Setting up IPs
- Edit ip_interface.config with relevant  values
#### on sender CX5
- ./scripts/setup/setup-ip.sh -n cx5 -h src 
- ./scripts/setup/setup-ip.sh -n cx5 -h src --assign-multiple-ips 
#### on receiver CX5
- ./scripts/setup/setup-ip.sh -n cx5 -h dst
- ./scripts/setup/setup-ip.sh -n cx5 -h dst --assign-multiple-ips
#### on sender FPGA
- ./scripts/setup/setup-ip.sh -n fpga -h src 
- ./scripts/setup/setup-ip.sh -n fpga -h src --assign-multiple-ips 
#### on receiver FPGA
- ./scripts/setup/setup-ip.sh -n fpga -h dst
- ./scripts/setup/setup-ip.sh -n fpga -h dst --assign-multiple-ips

### Settings up filter rules
#### on sender
- ./scripts/setup/remove_filters.sh -n cx5
- ./scripts/setup/remove_filters.sh -n fpga
- ./scripts/setup/add_filters.sh -n cx5
- ./scripts/setup/add_filters.sh -n fpga

### Add dummy rules
#### on sender
#### Edit sandia-experiment/scripts/setup/ip_interface.config with relevant values
- ./scripts/setup/dummy_filters.sh -n fpga








