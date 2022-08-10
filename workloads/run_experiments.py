import argparse
import json
import os 
from datetime import datetime
from collections import namedtuple, OrderedDict
from contextlib import contextmanager, ExitStack
import time

script_dir = os.path.dirname(__file__)

class Experiment:
    def __init__(self, exp):
        self.exp_time = (datetime.now().isoformat()
                            .replace(':','').replace('-','').split('.')[0])
        self.experiment = exp
    
    def run(self):
        with ExitStack() as stack:
            print("Running", self.exp_time)
            time.sleep(10)

def load_experiments(all_experiments):
    experiments = OrderedDict()
    for i in range(len(all_experiments)):
        experiment_id = "Exp-" +  str(i) 
        exp = Experiment(all_experiments[i])
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