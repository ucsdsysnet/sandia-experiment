from command import RemoteCommand, run_local_command, get_ssh_client, exec_command
import constant as c

def start_iperf_server(exp_obj, exp_template, workload, stack):
    log_name = { 'iperf_server' : '/tmp/iperf-server-{}-r{}-{}.csv'.format(exp_obj.id, exp_obj.iteration, exp_obj.exp_time)}
    exp_obj.append_logs(log_name)

    start_server_cmd = ('iperf3 --server '
                            '--bind {} '
                            '--port {} '
                            '--one-off '
                            '--logfile {} ').format(
                                exp_template['server_list'][0],
                                c.IPERF_SERVER_PORT,
                                log_name['iperf_server'])

    print("iperf server cmd>", start_server_cmd)

    start_server = RemoteCommand(start_server_cmd,
                                exp_template['server_list_wan'][0],
                                username=exp_template['username'],
                                logs=[log_name['iperf_server']],
                                key_filename=exp_template['key_filename'])

    stack.enter_context(start_server())

def start_iperf_clients(exp_obj, exp_template, workload, stack):
    log_name = { 'iperf_client' : '/tmp/iperf-client-{}-r{}-{}.csv'.format(exp_obj.id, exp_obj.iteration, exp_obj.exp_time)}
    exp_obj.append_logs(log_name)

    start_client_cmd = ('iperf3 --client {} '
                            '--port {} '
                            '--bind {} '
                            '--cport {} '
                            '--zerocopy '
                            '--json '
                            '--logfile {} ').format(
                                exp_template['server_list'][0],
                                c.IPERF_SERVER_PORT,
                                exp_template['client_list'][0],
                                c.IPERF_CLIENT_PORT,
                                log_name['iperf_client'])

    print("iperf client cmd>", start_client_cmd)

    #If the client is the control machine run as a local command
    

    #Only when client is a remote machine
    # start_client = RemoteCommand(
    #         start_client_cmd,
    #         exp_template['client_list_wan'][0],
    #         username=exp_template['username'],
    #         logs=[log_name['iperf_client']],
    #         key_filename=exp_template['key_filename'])
    
    # stack.enter_context(start_client())

def start_memcached_clients(experiment, workload):
    print("start memcached clients: ")

