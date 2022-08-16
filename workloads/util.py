import os
import subprocess
import json 
from command import RemoteCommand, run_local_command, get_ssh_client, exec_command
import constant as c
import re
import pandas as pd 

###################~~~~SERVER COMMANDS~~~~##########################

def get_iperf_server_cmd(server_ip, server_port, log_file_name):
    start_server_cmd = ('iperf3 --server '
                                    '--bind {} '
                                    '--port {} '
                                    '--one-off '
                                    '--json '
                                    '--logfile {} ').format(
                                        server_ip,
                                        server_port,
                                        log_file_name)
    return start_server_cmd

def get_iperf_client_cmd(server_ip, server_port, client_ip, client_port, log_file_name):
    start_client_cmd = ('iperf3 --client {} '
                                    '--port {} '
                                    '--bind {} '
                                    '--cport {} '
                                    '--zerocopy '
                                    '--json '
                                    '--logfile {} ').format(
                                        server_ip,
                                        server_port,
                                        client_ip,
                                        client_port,
                                        log_file_name)
    return start_client_cmd

############################~~~LOG IMPLEMENTATION~~~######################

def log_experiment_details(exp_obj, exp_template):
    # print(exp_template)
    log_name = { 'experiment_details' : '/tmp/experiment-details-{}-r{}-{}.json'.format(exp_obj.id, exp_obj.iteration, exp_obj.exp_time)}
    exp_obj.append_logs(log_name)
    with open(log_name['experiment_details'], 'w') as f:
        json.dump(exp_template, f)

def collect_iperf_logs(exp_obj, exp_template, workload):
    all_server_files = '*{}-r{}-{}.json"'.format(exp_obj.id, exp_obj.iteration, exp_obj.exp_time)
    
    cmd = 'scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i {} {}@{}:{} /tmp/'.format(
        exp_template['key_filename'],
        exp_template['username'],
        exp_template['server_list_wan'][0],
        os.path.join('"/tmp', all_server_files))

    print("collect server logs", cmd)
    subprocess.run(cmd, check=True, shell=True,
                    stdout = subprocess.DEVNULL,
                    stderr=subprocess.PIPE)
    #TODO: Copy client logs only if its on a remote location
    # print("collect_iperf_client_logs")

def collect_memcached_logs(exp_obj, exp_template, workload):
    print("collect_memcached_logs")

def get_log_name(name, instance, exp_id, iteration, exp_time, ext_type):
    log_id = get_log_id(name, instance)
    log_name = { log_id : '/tmp/{}-i{}-{}-r{}-{}.{}'.format(name, str(instance), exp_id, iteration, exp_time, ext_type)}
    return log_name

def get_log_id(name, instance):
    log_id = name+"-"+str(instance)
    return log_id

############################~~~STATISTICS~~~######################
def log_queue_status(period, exp_obj, exp_template):
    client_log_id = get_log_id(c.CLIENT_QUEUE_STATS, 0)
    if period == "start":
        client_log_name = get_log_name(c.CLIENT_QUEUE_STATS, 0, exp_obj.id, exp_obj.iteration, exp_obj.exp_time, c.CSV)
        exp_obj.append_logs(client_log_name)

        if exp_template['nic_type'] == c.CX5:
            write_queue_stats(period, 'tx')
            write_queue_stats(period, 'rx')
    else:
        if exp_template['nic_type'] == c.CX5:
            write_queue_stats(period, 'rx')
            # write_queue_stats(period, 'rx')

def write_queue_stats(period, tx_or_rx):
    #TODO: Get Iface based on IP
    #TODO: remote command when client is remote

    # df = pd.DataFrame(columns=['q_number', 'start_tx', 'start_rx', 'end_tx', 'end_rx'])
    df = pd.DataFrame()
    out_str = run_local_command('ethtool -S ens3f0 | grep "{}[0-9]*_packets"'.format(tx_or_rx), True)
    queues = out_str.split("\n")
    q_numbers = []
    for queue in queues:
        packets_per_queue = queue.split(':')
        q_number = extract_queue_number(packets_per_queue[0].strip())
        if q_number != 'all':
            q_numbers.append(q_number)
    df['q_number'] = q_numbers
    df['tx_or_rx'] = tx_or_rx
    print(df)

def extract_queue_number(queue_details):
    # print(re.findall(r'\b\d+\b', queue_details))
    q_number = ''.join(filter(str.isdigit, queue_details))
    if q_number.strip() == '':
        return 'all'
    else:
        return q_number
