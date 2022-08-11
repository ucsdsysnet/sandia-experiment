def start_iperf_server(exp_obj, exp_template, workload, stack):
    log_name = { 'iperf_server' : '/tmp/iperf-server-{}-r{}-{}.csv'.format(exp_obj.id, exp_obj.iteration, exp_obj.exp_time)}
    exp_obj.append_logs(log_name)
    print(exp_obj.all_logs)
    # start_server_cmd = ('iperf3 --server '
    #                         '--bind {} '
    #                         '--port {} '
    #                         '--one-off '
    #                         '--logfile {} ').format(
    #                             experiment['server_list'][0],
    #                             5100,
    #                             flow.server_log)
    # print("iperf server cmd>", start_server_cmd)
    # start_server = cctestbed.RemoteCommand(start_server_cmd,
    #                                     experiment.server.ip_wan,
    #                                     username=experiment.server.username,
    #                                     logs=[flow.server_log],
    #                                     key_filename=experiment.server.key_filename)
    # stack.enter_context(start_server())

def start_iperf_clients(experiment, workload):
    print("start iperf clients: ")

def start_memcached_clients(experiment, workload):
    print("start memcached clients: ")

