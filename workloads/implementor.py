from command import RemoteCommand, run_local_command, get_ssh_client, exec_command
import constant as c
from contextlib import contextmanager, ExitStack
import os
import logging
import util
import subprocess

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

def run_client_command(exp_template, start_client_cmd, log_id, log_name, stack):
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
                logs=[log_name[log_id]],
                key_filename=exp_template['key_filename'])
        stack.enter_context(start_client())

###################~~~~IPERF~~~~##########################

def start_iperf_server(exp_obj, exp_template, workload, stack):
    print("mode:", workload['mode'])
    if (workload['mode'] == c.CLUSTER_MODE):
        print("cluster mode server")
        parallel_processes = workload['parallel']
        server_port = c.IPERF_SERVER_PORT
        for x in range(1, parallel_processes+1):
            # print("x:", x)
            log_id = util.get_log_id(c.IPERF_SERVER_LOG_ID, x)
            log_name = util.get_log_name(c.TEMP_LOG_LOCATION, c.IPERF_SERVER_LOG_ID, x, exp_obj.id, exp_obj.exp_time, c.JSON)
            exp_obj.append_logs(log_name)

            server_base_ip = exp_template['server_list'][0]
            octets = server_base_ip.split('.')
            last_octet = int(octets[3]) + x
            server_ip = str(octets[0]) + "." + str(octets[1]) + "." + str(octets[2]) + "." + str(last_octet)
            start_server_cmd = util.get_iperf_server_cmd(server_ip, server_port, log_name[log_id])
            server_port = server_port + 1
            print("iperf server cmd>", start_server_cmd)

            start_server = RemoteCommand(start_server_cmd,
                                        exp_template['server_list_wan'][0],
                                        username=exp_template['username'],
                                        logs=[log_name[log_id]],
                                        key_filename=exp_template['key_filename'], sudo=False)

            stack.enter_context(start_server())
    else:
        print("server instances:", workload['server_instances'])
        server_instances = workload['server_instances']
        # if (len(exp_template['server_list']) == server_instances):
        server_port = c.IPERF_SERVER_PORT
        for x in range(server_instances):
            log_id = util.get_log_id(c.IPERF_SERVER_LOG_ID, x)
            log_name = util.get_log_name(c.TEMP_LOG_LOCATION, c.IPERF_SERVER_LOG_ID, x, exp_obj.id, exp_obj.exp_time, c.JSON)
            exp_obj.append_logs(log_name)

            start_server_cmd = util.get_iperf_server_cmd(exp_template['server_list'][0], server_port, log_name[log_id])
            server_port = server_port + 1

            print("iperf server cmd>", start_server_cmd)

            start_server = RemoteCommand(start_server_cmd,
                                        exp_template['server_list_wan'][0],
                                        username=exp_template['username'],
                                        logs=[log_name[log_id]],
                                        key_filename=exp_template['key_filename'])

            stack.enter_context(start_server())

def start_iperf_clients(exp_obj, exp_template, workload, stack):
    print("mode:", workload['mode'])
    if (workload['mode'] == c.CLUSTER_MODE):
        parallel_processes = workload['parallel']
        client_port = c.IPERF_CLIENT_PORT
        server_port = c.IPERF_SERVER_PORT

        for x in range(1, parallel_processes+1):
            log_id = util.get_log_id(c.IPERF_CLIENT_LOG_ID, x)
            log_name = util.get_log_name(c.TEMP_LOG_LOCATION, c.IPERF_CLIENT_LOG_ID, x, exp_obj.id, exp_obj.exp_time, c.JSON)
            exp_obj.append_logs(log_name)

            server_base_ip = exp_template['server_list'][0]
            octets = server_base_ip.split('.')
            last_octet = int(octets[3]) + x
            server_ip = str(octets[0]) + "." + str(octets[1]) + "." + str(octets[2]) + "." + str(last_octet)

            client_base_ip = exp_template['client_list'][0]
            c_octets = client_base_ip.split('.')
            c_last_octet = int(c_octets[3]) + x
            client_ip = str(c_octets[0]) + "." + str(c_octets[1]) + "." + str(c_octets[2]) + "." + str(c_last_octet)

            start_client_cmd = util.get_iperf_client_cmd(server_ip, 
                                                        server_port, 
                                                        client_ip,
                                                        client_port,
                                                        exp_template['duration'],
                                                        log_name[log_id])
            server_port = server_port + 1
            client_port = client_port + 1
            print("iperf client cmd>", start_client_cmd)
            run_client_command(exp_template, start_client_cmd, log_id, log_name, stack)

    else:
        client_instances = workload['clients']
        len_server_instances = workload['server_instances']
        client_port = c.IPERF_CLIENT_PORT
        server_port = c.IPERF_SERVER_PORT

        server_ports = [server_port]
        for i in range(len_server_instances-1):
            server_port = server_port + 1
            server_ports.append(server_port)

        print("server ports:", server_ports)

        for x in range(client_instances):
            log_id = util.get_log_id(c.IPERF_CLIENT_LOG_ID, x)
            log_name = util.get_log_name(c.TEMP_LOG_LOCATION, c.IPERF_CLIENT_LOG_ID, x, exp_obj.id, exp_obj.exp_time, c.JSON)
            exp_obj.append_logs(log_name)

            server_port_index = x % len_server_instances
            start_client_cmd = util.get_iperf_client_cmd(exp_template['server_list'][0], 
                                                        server_ports[server_port_index], 
                                                        exp_template['client_list'][0],
                                                        client_port,
                                                        exp_template['duration'],
                                                        log_name[log_id])

            print("iperf client cmd>", start_client_cmd)
            client_port = client_port + 1
            run_client_command(exp_template, start_client_cmd, log_id, log_name, stack)

###################~~~~MEMCACHED~~~~##########################

def start_memcached_clients(exp_obj, exp_template, workload, stack):
    print("start memcached clients: ")
    if (workload['mode'] == c.CLUSTER_MODE):
        print("cluster")
        parallel_processes = workload['parallel']
        server_port = c.MEMCACHED_SERVER_PORT
        for x in range(1, parallel_processes+1):
            log_id = util.get_log_id(c.MEMCACHED_CLIENT_LOG_ID, x)
            log_name = util.get_log_name(c.TEMP_LOG_LOCATION, c.MEMCACHED_CLIENT_LOG_ID, x, exp_obj.id, exp_obj.exp_time, c.JSON)
            exp_obj.append_logs(log_name)

            server_port = server_port + 1

            server_base_ip = exp_template['server_list'][0]
            octets = server_base_ip.split('.')
            last_octet = int(octets[3]) + x
            server_ip = str(octets[0]) + "." + str(octets[1]) + "." + str(octets[2]) + "." + str(last_octet)

            start_client_cmd = util.get_memcached_client_cmd(server_ip, 
                                                        server_port, 
                                                        log_name[log_id])
            print(start_client_cmd)
            run_client_command(exp_template, start_client_cmd, log_id, log_name, stack)
    else:
        client_instances = workload['clients']
        len_server_instances = workload['server_instances']
        server_port = c.MEMCACHED_SERVER_PORT
        server_ports = []
        # Multiple server instances assumes multiple IPs and ports
        for i in range(len_server_instances):
            server_port = server_port + 1
            server_ports.append(server_port)
        print(server_ports)
        for x in range(client_instances):
            log_id = util.get_log_id(c.MEMCACHED_CLIENT_LOG_ID, x)
            log_name = util.get_log_name(c.TEMP_LOG_LOCATION, c.MEMCACHED_CLIENT_LOG_ID, x, exp_obj.id, exp_obj.exp_time, c.JSON)
            exp_obj.append_logs(log_name)

            server_port_index = x % len_server_instances

            start_client_cmd = util.get_memcached_client_cmd(exp_template['server_list'][0], 
                                                        server_ports[server_port_index], 
                                                        log_name[log_id])
            print(start_client_cmd)
            run_client_command(exp_template, start_client_cmd, log_id, log_name, stack)

###################~~~~HIBENCH~~~~##########################

def remove_old_hibench_reports():
    os.system('rm -rf $HOME/sw/HiBench/report/hibench.report')

def start_hibench():
    start_hibench_cmd = "./workloads/hibench/start_hibench.sh"
    os.system(start_hibench_cmd)

def prepare_hibench_sort(exp_obj, exp_template, workload, stack):
    remove_old_hibench_reports()
    start_hibench()
    os.system('$HOME/sw/HiBench/bin/workloads/micro/sort/prepare/prepare.sh')

def run_hibench_sort(exp_obj, exp_template, workload, stack):
    start_client_cmd = '$HOME/sw/HiBench/bin/workloads/micro/sort/hadoop/run.sh'
    stack.enter_context(run_as_local_with_context(start_client_cmd))

def prepare_hibench_terasort(exp_obj, exp_template, workload, stack):
    remove_old_hibench_reports()
    start_hibench()
    os.system('$HOME/sw/HiBench/bin/workloads/micro/terasort/prepare/prepare.sh')

def run_hibench_terasort(exp_obj, exp_template, workload, stack):
    start_client_cmd = '$HOME/sw/HiBench/bin/workloads/micro/terasort/hadoop/run.sh'
    stack.enter_context(run_as_local_with_context(start_client_cmd))

###################~~~~SOCKPERF~~~~##########################
def start_sockperf_server(exp_obj, exp_template, workload, stack):
    print("Start sockperf server")
    sockperf_ipport_list_path = c.TEMP_LOG_LOCATION + "/" + c.SOCKPERF_IPPORT_LIST_FILENAME
    if (workload['mode'] == c.CLUSTER_MODE):
        parallel_processes = workload['parallel']
        server_port = c.SOCKPERF_SERVER_PORT
        for x in range(1, parallel_processes+1):
            server_base_ip = exp_template['server_list'][0]
            octets = server_base_ip.split('.')
            last_octet = int(octets[3]) + x
            server_ip = str(octets[0]) + "." + str(octets[1]) + "." + str(octets[2]) + "." + str(last_octet)
            print("server ip:port> {}:{}".format(server_ip, server_port))
            with open(sockperf_ipport_list_path, 'a') as f:
                f.write("{}:{}\n".format(server_ip, server_port))
            server_port = server_port + 1
    else:
        server_instances = workload['server_instances']
        server_port = c.SOCKPERF_SERVER_PORT
        for x in range(server_instances):
            server_base_ip = exp_template['server_list'][0]
            print("server ip:port> {}:{}".format(server_base_ip, server_port))
            with open(sockperf_ipport_list_path, 'a') as f:
                f.write("{}:{}\n".format(server_base_ip, server_port))
            server_port = server_port + 1

    # Copy sockperf ip:port list file to server
    cmd = 'scp -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -i {} {} {}@{}:{} '.format(
        exp_template['key_filename'],
        sockperf_ipport_list_path,
        exp_template['username'],
        exp_template['server_list_wan'][0],
        c.TEMP_LOG_LOCATION)

    subprocess.run(cmd, check=True, shell=True,
                    stdout = subprocess.DEVNULL,
                    stderr=subprocess.PIPE)

    start_server_cmd = "sockperf server -f {} --threads-num 32 ".format(sockperf_ipport_list_path)
    start_server = RemoteCommand(start_server_cmd,
                                exp_template['server_list_wan'][0],
                                username=exp_template['username'],
                                # logs=[log_name[log_id]],
                                key_filename=exp_template['key_filename'], sudo=False)

    stack.enter_context(start_server())

def start_sockperf_clients(exp_obj, exp_template, workload, stack):
    print("mode:", workload['mode'])
    if (workload['mode'] == c.CLUSTER_MODE):
        parallel_processes = workload['parallel']
        server_port = c.SOCKPERF_SERVER_PORT

        for x in range(1, parallel_processes+1):
            log_id = util.get_log_id(c.SOCKPERF_CLIENT_LOG_ID, x)
            log_name = util.get_log_name(c.TEMP_LOG_LOCATION, c.SOCKPERF_CLIENT_LOG_ID, x, exp_obj.id, exp_obj.exp_time, c.TXT)
            exp_obj.append_logs(log_name)

            server_base_ip = exp_template['server_list'][0]
            octets = server_base_ip.split('.')
            last_octet = int(octets[3]) + x
            server_ip = str(octets[0]) + "." + str(octets[1]) + "." + str(octets[2]) + "." + str(last_octet)

            start_client_cmd = util.get_sockperf_client_cmd(server_ip, 
                                                        server_port,
                                                        exp_template['duration'],
                                                        log_name[log_id])
            server_port = server_port + 1
            print("sockperf client cmd>", start_client_cmd)
            run_client_command(exp_template, start_client_cmd, log_id, log_name, stack)

    else:
        client_instances = workload['clients']
        len_server_instances = workload['server_instances']
        # client_port = c.IPERF_CLIENT_PORT
        # server_port = c.IPERF_SERVER_PORT

        # server_ports = [server_port]
        # for i in range(len_server_instances-1):
        #     server_port = server_port + 1
        #     server_ports.append(server_port)

        # print("server ports:", server_ports)

        # for x in range(client_instances):
        #     log_id = util.get_log_id(c.IPERF_CLIENT_LOG_ID, x)
        #     log_name = util.get_log_name(c.TEMP_LOG_LOCATION, c.IPERF_CLIENT_LOG_ID, x, exp_obj.id, exp_obj.exp_time, c.JSON)
        #     exp_obj.append_logs(log_name)

        #     server_port_index = x % len_server_instances
        #     start_client_cmd = util.get_iperf_client_cmd(exp_template['server_list'][0], 
        #                                                 server_ports[server_port_index], 
        #                                                 exp_template['client_list'][0],
        #                                                 client_port,
        #                                                 exp_template['duration'],
        #                                                 log_name[log_id])

        #     print("iperf client cmd>", start_client_cmd)
        #     client_port = client_port + 1
        #     run_client_command(exp_template, start_client_cmd, log_id, log_name, stack)