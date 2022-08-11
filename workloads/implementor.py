from command import RemoteCommand, run_local_command, get_ssh_client, exec_command

def start_iperf_server(exp_obj, exp_template, workload, stack):
    log_name = { 'iperf_server' : '/tmp/iperf-server-{}-r{}-{}.csv'.format(exp_obj.id, exp_obj.iteration, exp_obj.exp_time)}
    exp_obj.append_logs(log_name)

    start_server_cmd = ('iperf3 --server '
                            '--bind {} '
                            '--port {} '
                            '--one-off '
                            '--logfile {} ').format(
                                exp_template['server_list'][0],
                                5100,
                                log_name['iperf_server'])

    print("iperf server cmd>", start_server_cmd)

    start_server = RemoteCommand(start_server_cmd,
                                exp_template['server_list_wan'][0],
                                username=exp_template['username'],
                                logs=[log_name['iperf_server']],
                                key_filename=exp_template['key_filename'])

    stack.enter_context(start_server())

def start_iperf_clients(experiment, workload):
    print("start iperf clients: ")

def start_memcached_clients(experiment, workload):
    print("start memcached clients: ")

