from command import RemoteCommand, run_local_command, get_ssh_client, exec_command
import constant as c
from contextlib import contextmanager, ExitStack
import os
import logging

def start_iperf_server(exp_obj, exp_template, workload, stack):
    log_name = { 'iperf_server' : '/tmp/iperf-server-{}-r{}-{}.json'.format(exp_obj.id, exp_obj.iteration, exp_obj.exp_time)}
    exp_obj.append_logs(log_name)

    start_server_cmd = ('iperf3 --server '
                            '--bind {} '
                            '--port {} '
                            '--one-off '
                            '--json '
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

@contextmanager
def run_as_local_with_context(start_client_cmd):
    pid = None
    try:
        os.system(start_client_cmd + " &")
        # run_local_command(start_client_cmd, True)
        pid = run_local_command('pgrep -f "{}"'.format(start_client_cmd))
        if (pid is None or pid == ""):
            print("Iperf client PID is None or empty:", pid)
        else:
            print("Iperf client PID is: ", pid)
            # assert(pid)
            # pid = int(pid)
            # logging.info('PID={}'.format(pid))
            # yield pid
        yield
    except Exception as ex:
        print(False)
    # finally:
        # print("finally---")
        # logging.info('Cleaning up cmd: {}'.format(start_client_cmd))
        # run_local_command('kill {}'.format(pid))

def start_iperf_clients(exp_obj, exp_template, workload, stack):
    log_name = { 'iperf_client' : '/tmp/iperf-client-{}-r{}-{}.json'.format(exp_obj.id, exp_obj.iteration, exp_obj.exp_time)}
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
    out_str = run_local_command('ifconfig | grep -w {}'.format(exp_template['client_list'][0]), True)
    if out_str.find(exp_template['client_list'][0]) != -1:
        stack.enter_context(run_as_local_with_context(start_client_cmd))
    else:
        #Only when client is a remote machine
        start_client = RemoteCommand(
                start_client_cmd,
                exp_template['client_list_wan'][0],
                username=exp_template['username'],
                logs=[log_name['iperf_client']],
                key_filename=exp_template['key_filename'])
        stack.enter_context(start_client())

def start_memcached_clients(experiment, workload):
    print("start memcached clients: ")

