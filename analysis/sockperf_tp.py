import sys
sys.path.insert(0, 'workloads')
import analyzer as az 
import constant as c 
import pandas as pd

def calculate_throughput(log_list):
    throughput = 0
    for sockperf_log in log_list:
        with open(sockperf_log, 'r') as f:
            last_line = f.readlines()[-1]
            tp = last_line[last_line.find("(")+1:last_line.find(")")]
            vals = tp.split( )
            throughput = throughput + float(vals[0])
    return throughput


def populate_analyzer(analyzer):
    analyzer.sockperf_logs
    return analyzer

all_analysers = az.get_experiment_analysers(f"*{sys.argv[1]}*", sys.argv[2], sys.argv[3])
all_tp_gbps = 0
n = 0
for analyser_id in all_analysers:
    print("~~~~~",analyser_id, "~~~~~")
    analyzer = populate_analyzer(all_analysers[analyser_id])

    tp_gbps = calculate_throughput(analyzer.sockperf_log_list)
    all_tp_gbps = all_tp_gbps + tp_gbps
    print("Iteration {} Throughput - {} Gbps".format(n, tp_gbps))

    n = n + 1
    
print("Avg Throughput {} Gbps".format(str(all_tp_gbps/n)))