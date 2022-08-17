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
            df_start_merged = get_q_dataframe(period)
            df_start_merged.to_csv(client_log_name[client_log_id], header=False, index=True)
    else:
        if exp_template['nic_type'] == c.CX5:
            df_start = pd.read_csv(exp_obj.all_logs[0][client_log_id] ,sep=',', 
                    names=["q_number", "start_rx", "start_tx"])
            df_end = get_q_dataframe(period)
            different_start_cols = df_start.columns.difference(df_end.columns)
            df_start_cols = df_start[different_start_cols]
            df_all_merged = pd.merge(df_end, df_start_cols, left_index=True, right_index=True, how='inner')
            df_all_merged.to_csv(exp_obj.all_logs[0][client_log_id], header=True, index=True)
            
def get_queue_stats(period, tx_or_rx):
    #TODO: Get Iface based on IP
    #TODO: remote command when client is remote
    df = pd.DataFrame()
    out_str = run_local_command('ethtool -S {} | grep "{}[0-9]*_packets"'.format(c.CX5_IFNAME, tx_or_rx), True)
    queues = out_str.split("\n")
    q_numbers = []
    packets_per_queue = []
    for queue in queues:
        desc_packets = queue.split(':')
        q_number = extract_queue_number(desc_packets[0].strip())
        if q_number != 'all':
            q_numbers.append(q_number)
            packets_per_queue.append(desc_packets[1].strip())
    df['q_number'] = q_numbers
    header = period + "_" + tx_or_rx
    df[header] = packets_per_queue
    return df

def extract_queue_number(queue_details):
    # print(re.findall(r'\b\d+\b', queue_details))
    q_number = ''.join(filter(str.isdigit, queue_details))
    if q_number.strip() == '':
        return 'all'
    else:
        return q_number

def get_q_dataframe(period):
    df_tx = get_queue_stats(period, 'tx')
    df_rx = get_queue_stats(period, 'rx')
    different_tx_cols = df_tx.columns.difference(df_rx.columns)
    df_tx_cols = df_tx[different_tx_cols]
    df_merged = pd.merge(df_rx, df_tx_cols, left_index=True, right_index=True, how='inner')
    return df_merged