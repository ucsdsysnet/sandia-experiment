import sys
sys.path.insert(0, 'workloads')
import constant as c
import glob 
import os 
import re
from collections import namedtuple, OrderedDict
import tarfile
import json 
import pandas as pd 

class ExperimentAnalyzer:
    def __init__(self, tar_path, exp_identifier):
        self.tar_path = tar_path
        self.exp_id = exp_identifier
        self.data_process_path = c.DATAPATH_PROCESSED + self.exp_id

        self._experiment_log = None
        self._nic_queue_logs = None
        self._iperf_client_logs = None
        self._iperf_server_logs = None
        self._memcached_logs = None

        self.obj_experiment_details = None 
        self.df_nic_client_queue_stats = None 
        self.df_nic_server_queue_stats = None 

        self.obj_iperf_clients = []
        self.obj_iperf_servers = []
        self.obj_memcached = []

        tar = tarfile.open(self.tar_path, "r:gz")
        tar.extractall(self.data_process_path)
        tar.close()

    @property
    def experiment_log(self):
        exp_log_filter = self.data_process_path + "/" + c.EXPERIMENT_DETAILS_LOG_ID + "*"
        exp_log_list = glob.glob(exp_log_filter)
        with open(exp_log_list[0]) as f:
            exp_json = json.load(f)
            self.obj_experiment_details = exp_json

    @property
    def nic_queue_logs(self):
        client_q_log_filter = self.data_process_path + "/" + c.CLIENT_QUEUE_STATS + "*"
        client_q_log_list = glob.glob(client_q_log_filter)
        df_c_q = pd.read_csv(client_q_log_list[0] ,sep=',',)
        self.df_nic_client_queue_stats = df_c_q
        
        server_q_log_filter = self.data_process_path + "/" + c.SERVER_QUEUE_STATS + "*"
        server_q_log_list = glob.glob(server_q_log_filter)
        if server_q_log_list:
            df_s_q = pd.read_csv(server_q_log_list[0] ,sep=',',)
            self.df_nic_server_queue_stats = df_s_q

        # print(self.df_nic_client_queue_stats)
        # print(self.df_nic_server_queue_stats)

    @property
    def iperf_client_logs(self):
        client_log_filter = self.data_process_path + "/" + c.IPERF_CLIENT_LOG_ID + "*"
        iperf_client_log_list = glob.glob(client_log_filter)
        for client_log in iperf_client_log_list:
            with open(client_log) as f:
                client_json = json.load(f)
                self.obj_iperf_clients.append(client_json)
        # print(self.obj_iperf_clients)

    @property
    def iperf_server_logs(self):
        server_log_filter = self.data_process_path + "/" + c.IPERF_SERVER_LOG_ID + "*"
        iperf_server_log_list = glob.glob(server_log_filter)
        for server_log in iperf_server_log_list:
            with open(server_log) as f:
                server_json = json.load(f)
                self.obj_iperf_servers.append(server_json)

    @property
    def memcached_logs(self):
        memc_log_filter = self.data_process_path + "/" + c.MEMCACHED_CLIENT_LOG_ID + "*"
        memc_log_list = glob.glob(memc_log_filter)
        for memc_log in memc_log_list:
            with open(memc_log) as f:
                memc_json = json.load(f)
                self.obj_memcached.append(memc_json)
        # print(self.obj_memcached)
    
def load_experiments(experiment_name_patterns, tar_path):
    num_local_files = 0
    for experiment_name_pattern in experiment_name_patterns:
        local_filepaths = glob.glob(os.path.join(tar_path, experiment_name_pattern +'.tar.gz'))
        num_local_files += len(local_filepaths)
    experiment_analyzers = OrderedDict()
    for tarfile_localpath in local_filepaths:
        exp_identifier = tarfile_localpath.split('/')[3][:-7]
        experiment_analyzer = ExperimentAnalyzer(tarfile_localpath, exp_identifier)
        experiment_analyzers[exp_identifier] = experiment_analyzer
    return experiment_analyzers

def get_experiment_analysers(file_pattern, tar_path):
    experiment_analyzers = load_experiments(['*'+file_pattern+'*'], tar_path)
    return experiment_analyzers

# def populate_analyzer(analyzer):
#     analyzer.experiment_log
#     analyzer.nic_queue_logs
#     analyzer.iperf_client_logs
#     analyzer.iperf_server_logs
#     analyzer.memcached_logs
#     return analyzer

# all_analysers = get_experiment_analysers(f"*{sys.argv[1]}*", sys.argv[2])
# for analyser_id in all_analysers:
#     print("~~~~~",analyser_id, "~~~~~")
#     analyzer = populate_analyzer(all_analysers[analyser_id])