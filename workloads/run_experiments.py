import argparse
import json
import os 
from datetime import datetime
from collections import namedtuple, OrderedDict
from contextlib import contextmanager, ExitStack
import time
import implementor as impl

script_dir = os.path.dirname(__file__)

class Experiment:
    def __init__(self, id, exp):
        self.id = id

        #set name
        self.name = ""
        for workload_name in exp['workloads'][0].keys():
            self.name = self.name + "-" + workload_name

        self.exp_time = (datetime.now().isoformat()
                            .replace(':','').replace('-','').split('.')[0])
    
        self.experiment = exp

        self.iteration = 0
        self.all_logs = []
        self.logs = {
            # 'iperf_server': '/tmp/iperf-{}-{}.csv'.format("iperf", self.exp_time)
        }
    
    def append_logs(self, log_file):
        self.all_logs.append(log_file)

    def run(self, iteration):
        self.iteration = iteration
        with ExitStack() as stack:
            workloads = self.experiment['workloads']
            workload_types = workloads[0].keys()
            #Start servers
            for index, workload in enumerate(workload_types):
                #Assumption - memached server instances needs to be up and populated before running experiments
                server_switcher = {
                    'iperf': lambda: impl.start_iperf_server(self, self.experiment, workloads[0]["iperf"], stack)
                }
                func = server_switcher.get(workload, lambda: "Invalid Experiment!")
                func()
            
            #Run clients
            for index, workload in enumerate(workload_types):
                client_switcher = {
                    'iperf': lambda: impl.start_iperf_clients(self, self.experiment, workloads[0]["iperf"], stack),
                    'memcached': lambda: impl.start_memcached_clients(self.experiment, workloads[0]["memcached"])
                }
                func = client_switcher.get(workload, lambda: "Invalid Experiment!")
                func()
            # time.sleep(60)
    
    def get_repeat(self):
        return self.experiment['repeat']

def load_experiments(all_experiments):
    experiments = OrderedDict()
    for i in range(len(all_experiments)):
        experiment_id = "Exp" +  str(i) 
        exp = Experiment(experiment_id, all_experiments[i])
        experiments[experiment_id] = exp
    return experiments

def load_config_file(config_filename):
    """Parse json config file"""
    file_path = os.path.join(script_dir, config_filename)
    with open(file_path) as f:
        config = json.load(f)
    return config

def main(args):
    config = load_config_file(args.config_file)
    # print(config)
    print('Going to run {} experiments'.format(len(config['experiments'])))
    exps = load_experiments(config['experiments'])
    for experiment in exps.values():
        print("+++++++++++++++++", "Running Experiment:", experiment.id, "++++++++++++++++")
        for x in range(experiment.get_repeat()):
            experiment.run(x)

def parse_args():
    """Parse commandline arguments"""
    parser = argparse.ArgumentParser(description='Run Experiments')
    parser.add_argument('config_file', help='Configuration file describing experiment')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    main(args)