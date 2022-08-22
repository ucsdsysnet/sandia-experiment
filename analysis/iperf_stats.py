import sys
sys.path.insert(0, 'workloads')
import analyzer as az 
import constant as c 
import pandas as pd

def populate_analyzer(analyzer):
    analyzer.experiment_log
    # analyzer.nic_queue_logs
    analyzer.iperf_client_logs
    # analyzer.iperf_server_logs
    analyzer.memcached_logs
    return analyzer

#args - file_pattern, tar_location, data_process_location
all_analysers = az.get_experiment_analysers(f"*{sys.argv[1]}*", sys.argv[2], sys.argv[3])
all_ids = []
exp_sum_sent = []
exp_sum_received = []
for analyser_id in all_analysers:
    print("~~~~~",analyser_id, "~~~~~")
    analyzer = populate_analyzer(all_analysers[analyser_id])
    all_sum_sent_gbps = 0
    all_sum_received_gbps = 0
    for iperf_obj in analyzer.obj_iperf_clients:
        sum_sent_gbps = (iperf_obj['end']['sum_sent']['bits_per_second']) * c.BPS_TO_GBPS
        all_sum_sent_gbps = all_sum_sent_gbps + sum_sent_gbps
        sum_received_gbps = (iperf_obj['end']['sum_received']['bits_per_second']) * c.BPS_TO_GBPS
        all_sum_received_gbps = all_sum_received_gbps + sum_received_gbps
    all_ids.append(analyser_id)
    exp_sum_sent.append(all_sum_sent_gbps)
    exp_sum_received.append(all_sum_received_gbps)
    
df = pd.DataFrame()
df['exp_name'] = all_ids
df['all_sum_sent_gbps'] = exp_sum_sent
df['all_sum_received_gbps'] = exp_sum_received
print(df)
print('mean:', df['all_sum_sent_gbps'].mean())
print('std:', df['all_sum_sent_gbps'].std())

# df.to_csv('test.csv', header=False, index=True)
