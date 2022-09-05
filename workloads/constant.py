CLUSTER_MODE = "CLUSTER"
NORMAL_MODE = "NORMAL"
IP_MODE = "IP"

# Note: Both the client and the server should have the same location to store logs
TEMP_LOG_LOCATION = "/tmp"
TCPDUMP_LOCATION = "/mydata"

# Generic Log Names in template json
TXRX_LOG = "txrx_log"
TCPDUMP_LOG = "tcpdump"
CPU_UTIL_LOG = "cpu_util"
INTERRUPT_LOG = "interrupts"
QDISC_LOG = "qdisc_log"
FILTER_LOG = "filter_log"

# Generic Log IDs
EXPERIMENT_DETAILS_LOG_ID = "experiment-details"
CLIENT_TXRX_LOG_ID = "txrx-client"
SERVER_TXRX_LOG_ID = "txrx-server"
CLIENT_TCPDUMP_LOG_ID = "tcpdump-client"

JSON = "json"
CSV = "csv"
REPORT = "report"
PCAP = "pcap"

RUN_ON_CLIENT = "client"
RUN_ON_SERVER = "server"

CX5 = "cx5"

BPS_TO_GBPS = 0.000000001

# Iperf
IPERF_SERVER_PORT = 5100
IPERF_CLIENT_PORT = 5100 
IPERF_SERVER_LOG_ID = "iperf-server"
IPERF_CLIENT_LOG_ID = "iperf-client"

# Memcached
# Ports will start at 11211+1 = 11212
MEMCACHED_SERVER_PORT = 11211
MEMCACHED_CLIENT_LOG_ID = "memcached-client"
MEMCACHED_THREAD_COUNT = 1
MEMCACHED_CONNECTION_COUNT = 30
MEMCACHED_REQUEST_COUNT = 10000

# HiBench
HIBENCH_LOG_ID = "hibench-workload"