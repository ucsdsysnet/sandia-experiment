import sys
sys.path.insert(0, 'workloads')
import analyzer as az 
import constant as c 
import pandas as pd


def populate_analyzer(analyzer):
    analyzer.experiment_log
    analyzer.txrx_logs
    analyzer.memcached_logs
    return analyzer

#args - file_pattern, tar_location, data_process_location
all_analysers = az.get_experiment_analysers(f"*{sys.argv[1]}*", sys.argv[2], sys.argv[3])
all_ids = []
all_exp_ops = []
all_avg_p50 = []
all_avg_p99 = []
all_avg_p99_9 = []
for analyser_id in all_analysers:
    print("~~~~~",analyser_id, "~~~~~")
    all_ids.append(analyser_id)
    analyzer = populate_analyzer(all_analysers[analyser_id])
    sum_ops = 0
    sum_p50 = 0
    sum_p99 = 0
    sum_p99_9 = 0
    for mem_obj in analyzer.obj_memcached:
        ops = mem_obj['ALL STATS']['Gets']['Ops/sec']
        sum_ops = sum_ops + ops
        sum_p50 = sum_p50 + mem_obj['ALL STATS']['Gets']['Percentile Latencies']['p50.00']
        sum_p99 = sum_p99 + mem_obj['ALL STATS']['Gets']['Percentile Latencies']['p99.00']
        sum_p99_9 = sum_p99_9 + mem_obj['ALL STATS']['Gets']['Percentile Latencies']['p99.90']
    
    all_avg_p50.append(sum_p50 / len(analyzer.obj_memcached))
    all_avg_p99.append(sum_p99 / len(analyzer.obj_memcached))
    all_avg_p99_9.append(sum_p99_9 / len(analyzer.obj_memcached))
    all_exp_ops.append(sum_ops)

df = pd.DataFrame()
df['exp_name'] = all_ids
df['all_exp_ops'] = all_exp_ops
df['all_avg_p50'] = all_avg_p50
df['all_avg_p99'] = all_avg_p99
df['all_avg_p99_9'] = all_avg_p99_9
print(df)
print('mean ops:', df['all_exp_ops'].mean())
print('std ops:', df['all_exp_ops'].std())
print('mean p50:', df['all_avg_p50'].mean())
print('std ops p50:', df['all_avg_p50'].std())
print('mean p99:', df['all_avg_p99'].mean())
print('std ops p99:', df['all_avg_p99'].std())
print('mean p99.9:', df['all_avg_p99_9'].mean())
print('std ops p99.9:', df['all_avg_p99_9'].std())