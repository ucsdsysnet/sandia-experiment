import glob
import os
import tarfile
import json
import pandas as pd

DATAPATH_RAW="/home/dathapathu/experiments/data-tmp/"
DATAPATH_PROCESSED="/home/dathapathu/experiments/data-processed/"

def load_experiments(experiment_name_pattern):
    num_local_files = 0
    local_filepath = glob.glob(os.path.join(DATAPATH_RAW,experiment_name_pattern +'.tar'))
    print(local_filepath[0])
    if os.path.isfile(local_filepath[0]) and len(os.listdir(DATAPATH_PROCESSED)) == 0:
        print("Extracting tar...")
        my_tar = tarfile.open(local_filepath[0])
        my_tar.extractall(DATAPATH_PROCESSED)
        my_tar.close()

def get_summary(experiment_name_pattern, nic_type):
    instance_summary = pd.DataFrame(columns=['nic_type', 'instance_name', 'ops_sec', 'p50', 'p99', 'p99_9'])
    for x in range(101, 133):
        json_file_name = "memt-" + nic_type + "-" + str(x) + "-" + experiment_name_pattern + ".json"
        path_to_json = DATAPATH_PROCESSED + json_file_name
        # print(path_to_json)
        with open(path_to_json, 'r') as f:
            data = json.load(f)
            flow_summary = {}
            flow_summary['nic_type'] = nic_type
            flow_summary['instance_name'] = nic_type + "-" + str(x) + "-" + experiment_name_pattern
            flow_summary['ops_sec'] = data['ALL STATS']['Gets']['Ops/sec']
            flow_summary['p50'] = data['ALL STATS']['Gets']['Percentile Latencies']['p50.00']
            flow_summary['p99'] = data['ALL STATS']['Gets']['Percentile Latencies']['p99.00']
            flow_summary['p99_9'] = data['ALL STATS']['Gets']['Percentile Latencies']['p99.90']
            instance_summary = instance_summary.append(flow_summary, True)
            # print(flow_summary)
    print(instance_summary)

# load_experiments("*25-07-2022_095308*")
get_summary('25-07-2022_095308', 'cx5')