from command import RemoteCommand, run_local_command, get_ssh_client, exec_command
import constant as c
from contextlib import contextmanager, ExitStack
import os
import logging
import util 

def start_iperf_server(exp_obj, exp_template, workload, stack):
    print("cluster mode:", workload['cluster_mode'])
    if (workload['cluster_mode']):
        print("cluster mode server")
    else:
        print("server instances:", workload['server_instances'])
        server_instances = workload['server_instances']
        # if (len(exp_template['server_list']) == server_instances):
        server_port = c.IPERF_SERVER_PORT
        for x in range(server_instances):
            lod_id = 'iperf_server_'+str(x)
            log_name = { lod_id : '/tmp/iperf-server-i{}-{}-r{}-{}.json'.format(str(x), exp_obj.id, exp_obj.iteration, exp_obj.exp_time)}
            exp_obj.append_logs(log_name)

            start_server_cmd = util.get_iperf_server_cmd(exp_template['server_list'][0], server_port, log_name[lod_id])
            server_port = server_port + 1

            print("iperf server cmd>", start_server_cmd)

            start_server = RemoteCommand(start_server_cmd,
                                        exp_template['server_list_wan'][0],
                                        username=exp_template['username'],
                                        logs=[log_name[lod_id]],
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
    print("cluster mode:", workload['cluster_mode'])
    if (workload['cluster_mode']):
        print("cluster mode client")
    else:
        client_instances = workload['clients']
        print("client instances:", client_instances)
        len_server_instances = workload['server_instances']
        client_port = c.IPERF_CLIENT_PORT
        server_port = c.IPERF_SERVER_PORT

        server_ports = [server_port]
        for i in range(len_server_instances-1):
            server_port = server_port + 1
            server_ports.append(server_port)

        print("server ports:", server_ports)

        for x in range(client_instances):
            lod_id = 'iperf_client'+str(x)
            log_name = { lod_id : '/tmp/iperf-client-i{}-{}-r{}-{}.json'.format(str(x), exp_obj.id, exp_obj.iteration, exp_obj.exp_time)}
            exp_obj.append_logs(log_name)

            server_port_index = x % len_server_instances
            start_client_cmd = util.get_iperf_client_cmd(exp_template['server_list'][0], 
                                                        server_ports[server_port_index], 
                                                        exp_template['client_list'][0],
                                                        client_port,
                                                        log_name[lod_id])

            print("iperf client cmd>", start_client_cmd)

            client_port = client_port + 1

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
                        logs=[log_name[lod_id]],
                        key_filename=exp_template['key_filename'])
                stack.enter_context(start_client())

def start_memcached_clients(experiment, workload):
    print("start memcached clients: ")

