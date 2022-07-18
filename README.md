# iperf3 performance testing with `tc` rules for explicit TX queue mapping

## Host setup
### Hardware
- Identical src/dst nodes (yeti-03/04), each with:
    - 2 socket 20-core CPUs with HyperThreading (80 Linux cores total)
    - 256GB DRAM
- Both have a single 100G Mellanox ConnectX-5 NIC connected via a 100G Mellanox (Ethernet) switch.

### OS/Software
- Ubuntu 20.04.4 LTS
- Linux 5.13.0-39-generic
- `ofed_info -s`: MLNX_OFED_LINUX-5.5-1.0.3.2

### Scripts
- Run [install-dependencies.sh](./scripts/setup/install-dependencies.sh) to install dependencies, covered in the section below.
- Run [setup-generic.sh](./scripts/setup/setup-generic.sh) on both machines to tune for best performance. See script for detailed optimizations broken into separate functions.
- Run [setup-corundum.sh](./scripts/setup/setup-curundum.sh) on both machines if you are using FPGA NICs.
- Run [setup-cx5.sh](./scripts/setup/setup-cx5.sh) on both machines if you are using CX5 NICs.
- Run [setup-src-host.sh](./scripts/setup/setup-src-host.sh) `--enable-tc-mapping` to add `tc` TX queue mapping rules for each IP. See comments in script for details.
    - (Old) <s>You can use `--assign-multiple-ips` on sender side if using `src ip` match rules in `tc filter`. See notes in this script for details. In that case, you need to use `-B $bind_src_ip` in [run-iperf-clients.sh](./scripts/run-iperf/run-iperf-clients.sh)** to properly bind each client to a particular src ip.</s>
- Run [setup-dst-host.sh](./scripts/setup/setup-dst-host.sh) `--assign-multiple-ips` to add multiple IPs on the destination host. We can further scale this with more IPs/interface or more machines.

### Dependencies
- [Mellanox OFED packages](https://network.nvidia.com/products/infiniband-drivers/linux/mlnx_ofed/)
- [Mellanox IRQ Affinity Configuration Tool](http://www.mellanox.com/relateddocs/prod_software/mlnx_irq_affinity.tgz) from [Performance Tuning Guidelines
for Mellanox Network Adapters](https://network.nvidia.com/pdf/prod_software/Performance_Tuning_Guide_for_Mellanox_Network_Adapters_Archive.pdf) manual
- `numactl` for pinning processes to local NUMA domain

## `iperf3` testing
### Process
- We run multiple concurrent `iperf3` processes in order to use multiple cores, as the default multithread mode `iperf3 -P <num-threads>` seems to be limited to a single core.
- The following scripts manages multiple `iperf3` client/server processes and reports the aggregate throughput on the client side.
    - On server side / destination host, run [run-iperf-servers.sh](./scripts/run-iperf/run-iperf-servers.sh) `-p <num-processes>`, which starts up separate `iperf3` server processes using distinct consecutive ports and keeps them in the background.
    - The on client side / source host, run
        - [run-iperf-clients.sh](./scripts/run-iperf/run-iperf-clients.sh) `-p <num-processes> -s <server-ip>` for single IP mode, or
        - [run-iperf-clients.sh](./scripts/run-iperf/run-iperf-clients.sh) `-p <num-processes> -s <server-ip-base> --separate-servers` for accessing iperf processes with multiple IPs.
        Note that `<server-ip-base>` is one less than the first destination IP, which in my case was `10.0.0.200`, since [setup-dst-host.sh](./scripts/setup/setup-dst-host.sh) set the IPs starting from `10.0.0.201`.
    - Client `iperf3` processes will exit normally, whereas server `iperf3` processes can be manually killed using [kill-iperf-processes.sh](./scripts/run-iperf/kill-iperf-processes.sh).
- CPU utilization is "measured" by watching `top/htop`.

### Verification
We can verify that per-TX-queue mapping filters worked by checking these counters before/after the runs:
- `ethtool -S <iface> | grep "tx[0-9]*_packets"`
- `tc -s filter show dev <iface> egress`
