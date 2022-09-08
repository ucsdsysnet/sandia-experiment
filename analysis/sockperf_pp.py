import sys
sys.path.insert(0, 'workloads')
import analyzer as az 
import constant as c 
import pandas as pd

# Avg 99.9 latency of all flows in a single experiment
def latency_ping_pong(log_list):
    all_latency = 0
    i = 0
    for sockperf_log in log_list:
        with open(sockperf_log, 'r') as f:
            for num, line in enumerate(f, 1):
                if " percentile 99.900 " in line:
                    vals = line.split("=")
                    pp_latency = float(vals[1])
                    all_latency = all_latency + pp_latency
                    i = i + 1
    return (all_latency/i)

def populate_analyzer(analyzer):
    analyzer.sockperf_logs
    return analyzer

all_analysers = az.get_experiment_analysers(f"*{sys.argv[1]}*", sys.argv[2], sys.argv[3])
all_pp_latency = 0
n = 0
for analyser_id in all_analysers:
    print("~~~~~",analyser_id, "~~~~~")
    analyzer = populate_analyzer(all_analysers[analyser_id])
    latency_pp = latency_ping_pong(analyzer.sockperf_log_list)
    all_pp_latency = all_pp_latency + latency_pp
    n = n + 1
    
print("Avg p99.9 Ping Pong Latency {} μs".format(str(all_pp_latency/n)))