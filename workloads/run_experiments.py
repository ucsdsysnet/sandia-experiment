import argparse
import json
import os 
from datetime import datetime
from collections import namedtuple, OrderedDict
from contextlib import contextmanager, ExitStack
import time
import implementor as impl
import util
import logging
import subprocess

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
        self.tar_filename = "{}-{}-r{}-{}.tar.gz".format(self.id, self.name, str(self.iteration), self.exp_time)
        
    
    def append_logs(self, log_file):
        self.all_logs.append(log_file)

    def run(self, iteration):
        self.iteration = iteration
        with ExitStack() as stack:

            util.log_queue_status("start", self, self.experiment)

            workloads = self.experiment['workloads']
            workload_types = workloads[0].keys()
            #Start servers
            for index, workload in enumerate(workload_types):
                #Assumption - memached server instances needs to be up and populated before running experiments
                server_switcher = {
                    'iperf': lambda: impl.start_iperf_server(self, self.experiment, workloads[0]["iperf"], stack)
                }
                func = server_switcher.get(workload, lambda: "Invalid Server!")
                func()
            
            #Run clients
            for index, workload in enumerate(workload_types):
                client_switcher = {
                    'iperf': lambda: impl.start_iperf_clients(self, self.experiment, workloads[0]["iperf"], stack),
                    'memcached': lambda: impl.start_memcached_clients(self.experiment, workloads[0]["memcached"])
                }
                func = client_switcher.get(workload, lambda: "Invalid Client Experiment!")
                func()
            time.sleep(30)
            #Collect logs
            for index, workload in enumerate(workload_types):
                log_switcher = {
                    'iperf': lambda: util.collect_iperf_logs(self, self.experiment, workloads[0]["iperf"]),
                    'memcached': lambda: util.collect_memcached_logs(self, self.experiment, workloads[0]["memcached"])
                }
                func = log_switcher.get(workload, lambda: "Invalid Log Collector!")
                func()
        util.log_experiment_details(self, self.experiment)
        self.compress_logs()

    def compress_logs(self):
        print("compress logs")
        logs_to_compress = []
        # print(self.all_logs)
        for log in self.all_logs:
            # print(log)
            all_keys = log.keys()
            for index, key in enumerate(all_keys):
                # print(log[key])
                if os.path.isfile(log[key]):
                    logs_to_compress += [os.path.basename(log[key])]
        if len(logs_to_compress) == 0:
            logging.warning('Found no logs for this experiment to compress')
        else:
            logging.info('Compressing {} logs into tarfile: {}'.format(len(logs_to_compress), self.tar_filename))
            # print(logs_to_compress)
            cmd = 'cd /tmp && tar -czf {} {} && rm -f {}'.format(
                os.path.basename(self.tar_filename),
                ' '.join(logs_to_compress),
                ' && rm -f '.join(logs_to_compress))
            proc = subprocess.Popen(cmd, shell=True)
            logging.info('Running background command: {} (PID={})'.format(cmd, proc.pid))
        

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