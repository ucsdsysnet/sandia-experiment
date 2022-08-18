import sys
sys.path.insert(0, 'workloads')
import constant as c
import glob 
import os 
import re
from collections import namedtuple, OrderedDict

class ExperimentAnalyzer:
    def __init__(self, tar_path):
        self.tar_path = tar_path
        self._iperf_client_logs = None
        self._iperf_server_logs = None
        self._memcached_logs = None

    @property
    def iperf_client_logs(self):
        print("iperf_client_logs")

def load_experiments(experiment_name_patterns):
    num_local_files = 0
    for experiment_name_pattern in experiment_name_patterns:
        local_filepaths = glob.glob(os.path.join(c.DATAPATH_RAW,
                                                    experiment_name_pattern +'.tar.gz'))
        num_local_files += len(local_filepaths)
    experiment_analyzers = OrderedDict()
    for tarfile_localpath in local_filepaths:
        # print(tarfile_localpath)
        experiment_analyzer = ExperimentAnalyzer(tarfile_localpath)
        exp_identifier = tarfile_localpath.split('/')[3][:-7]
        experiment_analyzers[exp_identifier] = experiment_analyzer
    return experiment_analyzers

def get_experiment_analysers(file_pattern):
    experiment_analyzers = load_experiments(['*'+file_pattern+'*'])
    return experiment_analyzers

all_analysers = get_experiment_analysers(f"*{sys.argv[1]}*")
for analyser in all_analysers:
    print("~~~~~",analyser, "~~~~~")
    all_analysers[analyser].iperf_client_logs