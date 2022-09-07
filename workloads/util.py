import os
import subprocess
import json 
from command import RemoteCommand, run_local_command, get_ssh_client, exec_command
import constant as c
import re
import pandas as pd 

###################~~~~WORKLOAD COMMANDS~~~~##########################

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

def get_iperf_client_cmd(server_ip, server_port, client_ip, client_port, duration, log_file_name):
    start_client_cmd = ('iperf3 --client {} '
                                    '--port {} '
                                    '--bind {} '
                                    '--cport {} '
                                    '--zerocopy '
                                    '--time {} '
                                    '--json '
                                    '--logfile {} ').format(
                                        server_ip,
                                        server_port,
                                        client_ip,
                                        client_port,
                                        duration, 
                                        log_file_name)
    return start_client_cmd

def get_memcached_client_cmd(server_ip, server_port, log_file_name):
    start_client_cmd = ('memtier_benchmark -s {} '
                                    '-p {} '
                                    '-P memcache_text '
                                    '--ratio=0:1 '
                                    '-t {} '
                                    '-c {} '
                                    '-n {} '
                                    '--json-out-file {} ').format(
                                    server_ip,
                                    server_port, 
                                    c.MEMCACHED_THREAD_COUNT, 
                                    c.MEMCACHED_CONNECTION_COUNT,
                                    c.MEMCACHED_REQUEST_COUNT, 
                                    log_file_name)
    return start_client_cmd

def get_sockperf_client_tp_cmd(sock_mode, server_ip, server_port, duration, log_file_name):
    start_client_cmd = ('sockperf {} '
                            '-i {} '
                            '-p {} '
                            '--time {} '
                            '--msg-size=1472 '
                            '--mps=max '
                            '--giga-size >> {} ').format(
                                sock_mode,
                                server_ip,
                                server_port,
                                duration, 
                                log_file_name)
    return start_client_cmd
    
############################~~~LOG IMPLEMENTATION~~~######################

def log_experiment_details(exp_obj, exp_template):
    # print(exp_template)
    log_id = get_log_id(c.EXPERIMENT_DETAILS_LOG_ID, 0)
    log_name = get_log_name(c.TEMP_LOG_LOCATION, c.EXPERIMENT_DETAILS_LOG_ID, 0, exp_obj.id, exp_obj.exp_time, c.JSON)
    exp_obj.append_logs(log_name)
    with open(log_name[log_id], 'w') as f:
        json.dump(exp_template, f)

def collect_iperf_logs(exp_obj, exp_template, workload):
    all_server_files = '*{}-{}.json"'.format(exp_obj.id, exp_obj.exp_time)
    
    cmd = 'scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i {} {}@{}:{} {}/'.format(
        exp_template['key_filename'],
        exp_template['username'],
        exp_template['server_list_wan'][0],
        os.path.join('"{}'.format(c.TEMP_LOG_LOCATION), all_server_files),
        c.TEMP_LOG_LOCATION)

    print("collect server logs", cmd)
    subprocess.run(cmd, check=True, shell=True,
                    stdout = subprocess.DEVNULL,
                    stderr=subprocess.PIPE)
    #TODO: Copy client logs only if its on a remote location
    # print("collect_iperf_client_logs")

def collect_memcached_logs(exp_obj, exp_template, workload):
    print("collect_memcached_logs")

def collect_hibench_report(exp_obj, exp_template):
    print('collect HiBench Report')
    log_id = get_log_id(c.HIBENCH_LOG_ID, 0)
    log_name = get_log_name(c.TEMP_LOG_LOCATION, c.HIBENCH_LOG_ID, 0, exp_obj.id, exp_obj.exp_time, c.REPORT)
    hibench_log_cmd = 'mv $HOME/sw/HiBench/report/hibench.report {}'.format(log_name[log_id])
    print(hibench_log_cmd)
    os.system(hibench_log_cmd)
    exp_obj.append_logs(log_name)

def get_log_name(location, name, instance, exp_id, exp_time, ext_type):
    log_id = get_log_id(name, instance)
    log_name = { log_id : '{}/{}-i{}-{}-{}.{}'.format(location, name, str(instance), exp_id, exp_time, ext_type)}
    return log_name

def get_log_id(name, instance):
    log_id = name+"-"+str(instance)
    return log_id

def start_logs(exp_obj, exp_template, client_logs, server_logs):
    print('start log - {} {}'.format(client_logs, server_logs))
    
    if client_logs.__contains__(c.TXRX_LOG):
        log_queue_status("start", exp_obj, exp_template, c.RUN_ON_CLIENT, c.CLIENT_TXRX_LOG_ID)
    if client_logs.__contains__(c.TCPDUMP_LOG):
        # run_tcpdump_local(exp_obj, exp_template)
        print('client {} NOT IMPLEMENTED'.format(c.TCPDUMP_LOG))
    if client_logs.__contains__(c.CPU_UTIL_LOG):
        print('client {} NOT IMPLEMENTED'.format(c.CPU_UTIL_LOG))
    if client_logs.__contains__(c.INTERRUPT_LOG):
        print('client {} NOT IMPLEMENTED'.format(c.INTERRUPT_LOG))
    if client_logs.__contains__(c.QDISC_LOG):
        print('client {} NOT IMPLEMENTED'.format(c.QDISC_LOG))
    if client_logs.__contains__(c.FILTER_LOG):
        print('client {} NOT IMPLEMENTED'.format(c.FILTER_LOG))

    if server_logs.__contains__(c.TXRX_LOG):
        log_queue_status("start", exp_obj, exp_template, c.RUN_ON_SERVER, c.SERVER_TXRX_LOG_ID)
    if server_logs.__contains__(c.TCPDUMP_LOG):
        print('server {} NOT IMPLEMENTED'.format(c.TCPDUMP_LOG))
    if server_logs.__contains__(c.CPU_UTIL_LOG):
        print('server {} NOT IMPLEMENTED'.format(c.CPU_UTIL_LOG))
    if server_logs.__contains__(c.INTERRUPT_LOG):
        print('server {} NOT IMPLEMENTED'.format(c.INTERRUPT_LOG))
    if server_logs.__contains__(c.QDISC_LOG):
        print('server {} NOT IMPLEMENTED'.format(c.QDISC_LOG))
    if server_logs.__contains__(c.FILTER_LOG):
        print('server {} NOT IMPLEMENTED'.format(c.FILTER_LOG))

def stop_logs(exp_obj, exp_template, client_logs, server_logs):
    print('stop log - {} {}'.format(client_logs, server_logs))
    if client_logs.__contains__(c.TXRX_LOG):
        log_queue_status("end", exp_obj, exp_template, c.RUN_ON_CLIENT, c.CLIENT_TXRX_LOG_ID)
    if client_logs.__contains__(c.TCPDUMP_LOG):
        kill_tcpdump_local()

    if server_logs.__contains__(c.TXRX_LOG):
        log_queue_status("end", exp_obj, exp_template, c.RUN_ON_SERVER, c.SERVER_TXRX_LOG_ID)

def run_tcpdump_local(exp_obj, exp_template):
    client_log_id = get_log_id(c.CLIENT_TCPDUMP_LOG_ID, 0)
    iface_name = get_interface_name(exp_template['client_list'][0])
    client_log_name = get_log_name(c.TCPDUMP_LOCATION, c.CLIENT_TCPDUMP_LOG_ID, 0, exp_obj.id, exp_obj.exp_time, c.PCAP)
    exp_obj.append_logs(client_log_name)
    start_tcpdump_cmd = ('sudo tcpdump -n --packet-buffered '
                                 '--snapshot-length=65535 '
                                 '--interface={} '
                                 '-w {}'.format(iface_name, client_log_name[client_log_id]))
    os.system(start_tcpdump_cmd + " &")

def kill_tcpdump_local():
    run_local_command('sudo pkill -9 tcpdump', True)

############################~~~STATISTICS~~~######################
def log_queue_status(period, exp_obj, exp_template, run_on, logid):
    print("iteration:", period, exp_obj.iteration)
    log_id = get_log_id(logid, 0)
    iface_name = get_interface_name(exp_template['client_list'][0])
    if period == "start":
        log_name = get_log_name(c.TEMP_LOG_LOCATION, logid, 0, exp_obj.id, exp_obj.exp_time, c.CSV)
        exp_obj.append_logs(log_name)

        if exp_template['nic_type'] == c.CX5:
            df_start_merged = get_q_dataframe(period, iface_name, run_on, exp_template)
            df_start_merged.to_csv(log_name[log_id], header=False, index=True)
    else:
        if exp_template['nic_type'] == c.CX5:
            for log in exp_obj.all_logs:
                keysList = list(log.keys())
                if log_id in keysList:
                    print("correct txrx log:", log[log_id])
                    df_start = pd.read_csv(log[log_id] ,sep=',', 
                            names=["q_number", "start_rx", "start_tx"])
                    df_end = get_q_dataframe(period, iface_name, run_on, exp_template)
                    different_start_cols = df_start.columns.difference(df_end.columns)
                    df_start_cols = df_start[different_start_cols]
                    df_all_merged = pd.merge(df_end, df_start_cols, left_index=True, right_index=True, how='inner')
                    df_all_merged.to_csv(log[log_id], header=True, index=True)
            
def get_queue_stats(period, iface_name, tx_or_rx, run_on, exp_template):
    #TODO: remote command when client is remote
    df = pd.DataFrame()
    if (run_on == c.RUN_ON_CLIENT):
        out_str = run_local_command('ethtool -S {} | grep "{}[0-9]*_packets"'.format(iface_name, tx_or_rx), True)
    if (run_on == c.RUN_ON_SERVER):
        cmd = 'ethtool -S {} | grep "{}[0-9]*_packets"'.format(iface_name, tx_or_rx)
        print("run on server: {}".format(cmd))
        with get_ssh_client(ip_addr=exp_template['server_list_wan'][0],
                                username=exp_template['username'],
                                key_filename=exp_template['key_filename']) as ssh_client:
            _, stdout, stderr = exec_command(ssh_client,
                                                 exp_template['server_list_wan'][0],
                                                 cmd)
            # actually should return a bad exit status
            # exit_status =  stdout.channel.recv_exit_status()
            stdout_str = stdout.read()
            out_str = stdout_str.decode("utf-8") 
            # print("server out_str: {}".format(out_str))
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
    q_number = ''.join(filter(str.isdigit, queue_details))
    if q_number.strip() == '':
        return 'all'
    else:
        return q_number

def get_q_dataframe(period, iface_name, run_on, exp_template):
    df_tx = get_queue_stats(period, iface_name, 'tx', run_on, exp_template)
    df_rx = get_queue_stats(period, iface_name, 'rx', run_on, exp_template)
    different_tx_cols = df_tx.columns.difference(df_rx.columns)
    df_tx_cols = df_tx[different_tx_cols]
    df_merged = pd.merge(df_rx, df_tx_cols, left_index=True, right_index=True, how='inner')
    return df_merged

def get_interface_name(ip_addr):
    out_str = run_local_command("netstat -ie | grep -B1 {} | head -n1 | awk '{{print $1}}'".format(ip_addr), True)
    return out_str.strip()[:-1]