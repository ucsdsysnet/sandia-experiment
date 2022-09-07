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
import constant as c
import copy

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
        self.tar_filename = "{}-{}-{}.tar.gz".format(self.id, self.name, self.exp_time)
        self.completed_experiment_procs = []
        
    def append_logs(self, log_file):
        self.all_logs.append(log_file)

    def run(self):
        with ExitStack() as stack:

            util.start_logs(self, self.experiment, self.experiment['client_logs'], self.experiment['server_logs'])

            workloads = self.experiment['workloads']
            workload_types = workloads[0].keys()
            
            #Start servers
            for index, workload in enumerate(workload_types):
                #Assumption - memached server instances needs to be up and populated before running experiments memcached experiments
                server_switcher = {
                    'iperf': lambda: impl.start_iperf_server(self, self.experiment, workloads[0]["iperf"], stack),
                    'sockperf': lambda: impl.start_sockperf_server(self, self.experiment, workloads[0]["sockperf"], stack),
                    'hibench-sort': lambda: impl.prepare_hibench_sort(self, self.experiment, None, stack),
                    'hibench-terasort': lambda: impl.prepare_hibench_terasort(self, self.experiment, None, stack)
                }
                func = server_switcher.get(workload, lambda: "Invalid Server!")
                func()
            
            #Run clients
            for index, workload in enumerate(workload_types):
                client_switcher = {
                    'iperf': lambda: impl.start_iperf_clients(self, self.experiment, workloads[0]["iperf"], stack),
                    'sockperf': lambda: impl.start_sockperf_clients(self, self.experiment, workloads[0]["sockperf"], stack),
                    'memcached': lambda: impl.start_memcached_clients(self, self.experiment, workloads[0]["memcached"], stack),
                    'hibench-sort': lambda: impl.run_hibench_sort(self, self.experiment, None, stack),
                    'hibench-terasort': lambda: impl.run_hibench_terasort(self, self.experiment, None, stack)
                }
                func = client_switcher.get(workload, lambda: "Invalid Client Experiment!")
                func()
            time.sleep(self.experiment['duration'] + 5)

            #Collect logs
            for index, workload in enumerate(workload_types):
                log_switcher = {
                    'iperf': lambda: util.collect_iperf_logs(self, self.experiment, workloads[0]["iperf"]),
                    'memcached': lambda: util.collect_memcached_logs(self, self.experiment, workloads[0]["memcached"])
                }
                func = log_switcher.get(workload, lambda: "Invalid Log Collector!")
                func()

        if workload_types.__contains__('hibench-sort') or workload_types.__contains__('hibench-terasort'): 
            stop_hibench_cmd = "./workloads/hibench/stop_hibench.sh"
            os.system(stop_hibench_cmd)
            util.collect_hibench_report(self, self.experiment)

        util.log_experiment_details(self, self.experiment)
        util.stop_logs(self, self.experiment, self.experiment['client_logs'], self.experiment['server_logs'])
        self.compress_logs()
        self.cleanup_experiments()

    def compress_logs(self):
        print("compress logs")
        logs_to_compress = []
        for log in self.all_logs:
            all_keys = log.keys()
            for index, key in enumerate(all_keys):
                if os.path.isfile(log[key]):
                    logs_to_compress += [os.path.basename(log[key])]
        if len(logs_to_compress) == 0:
            logging.warning('Found no logs for this experiment to compress')
        else:
            logging.info('Compressing {} logs into tarfile: {}'.format(len(logs_to_compress), self.tar_filename))
            cmd = 'cd {} && tar -czf {} {} && rm -f {}'.format(
                c.TEMP_LOG_LOCATION,
                os.path.basename(self.tar_filename),
                ' '.join(logs_to_compress),
                ' && rm -f '.join(logs_to_compress))
            proc_compress = subprocess.Popen(cmd, shell=True)
            self.append_processes(proc_compress)
            os.makedirs(self.experiment['tar_location'], exist_ok = True)
            proc_mov = subprocess.Popen('mv {}/{} {}'.format(c.TEMP_LOG_LOCATION, self.tar_filename, self.experiment['tar_location']), shell=True)
            self.append_processes(proc_mov)
        # Remove sockperf ip:port list file
        sockperf_ipport_list_path = c.TEMP_LOG_LOCATION + "/" + c.SOCKPERF_IPPORT_LIST_FILENAME
        subprocess.Popen("rm -rf {}".format(sockperf_ipport_list_path), shell=True)
        
    def append_processes(self, proc):
        if proc == -1:
            print('Proc is -1')
        elif proc is not None:
            self.completed_experiment_procs.append(proc)

    def cleanup_experiments(self):
        for proc in self.completed_experiment_procs:
            logging.info('Waiting for subprocess to finish PID={}'.format(proc.pid))
            proc.wait()
            if proc.returncode != 0:
                logging.warning('Error cleaning up experiment PID={}'.format(proc.pid))

    def get_repeat(self):
        return self.experiment['repeat']

    def set_iteration(self, iteration):
        self.iteration = iteration

def load_experiments(all_experiments):
    experiments = OrderedDict()
    for i in range(len(all_experiments)):
        for x in range(all_experiments[i]['repeat']):
            experiment_id = "Exp" +  str(i) + "-r" + str(x)
            exp = Experiment(experiment_id, all_experiments[i])
            exp.set_iteration(x)
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
        experiment.run()

def parse_args():
    """Parse commandline arguments"""
    parser = argparse.ArgumentParser(description='Run Experiments')
    parser.add_argument('config_file', help='Configuration file describing experiment')
    args = parser.parse_args()
    return args

if __name__ == '__main__':
    args = parse_args()
    main(args)