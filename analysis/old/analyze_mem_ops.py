import pandas as pd
import plotly
import plotly.graph_objects as go
import plotly.express as px

BASE_PATH = "/home/dathapathu/experiments/"

DATAPATH_SUMMARY = BASE_PATH+"data-summary/"

cx5_c11_path = BASE_PATH + "data-summary/" + "summary-c11-cx5.csv"
cx5_c22_path = BASE_PATH + "data-summary/" + "summary-c22-cx5.csv"
fpga_c11_path = BASE_PATH + "data-summary/" + "summary-c11-fpga.csv"
fpga_c22_path = BASE_PATH + "data-summary/" + "summary-c22-fpga.csv"

def plot_ops_summary(df):
    fig = px.bar(df, x='type', y='Ops')
    # fig.show()
    return fig

def get_instance_id(instance):
    instance_part = instance.split('-', 3)
    return instance_part[1]

def load_summary():
    cx5_c11 = pd.read_csv(cx5_c11_path, sep=',', header=0, names=["index", "nic_type", "instance_name", "ops_sec", "p50", "p99", "p99_9"])
    cx5_c11['instance_id'] = cx5_c11['instance_name'].apply(get_instance_id)
    
    cx5_c22 = pd.read_csv(cx5_c22_path, sep=',', header=0, names=["index", "nic_type", "instance_name", "ops_sec", "p50", "p99", "p99_9"])
    cx5_c22['instance_id'] = cx5_c22['instance_name'].apply(get_instance_id)

    fpga_c11 = pd.read_csv(fpga_c11_path, sep=',', header=0, names=["index", "nic_type", "instance_name", "ops_sec", "p50", "p99", "p99_9"])
    fpga_c11['instance_id'] = fpga_c11['instance_name'].apply(get_instance_id)

    fpga_c22 = pd.read_csv(fpga_c22_path, sep=',', header=0, names=["index", "nic_type", "instance_name", "ops_sec", "p50", "p99", "p99_9"])
    fpga_c22['instance_id'] = fpga_c22['instance_name'].apply(get_instance_id)

    cx5_c11_ops = cx5_c11['ops_sec'].sum()
    cx5_c22_ops = cx5_c22['ops_sec'].sum()
    fpga_c11_ops = fpga_c11['ops_sec'].sum()
    fpga_c22_ops = fpga_c22['ops_sec'].sum()

    data_ops = {'type': ['cx5_c11_ops', 'cx5_c22_ops', 'fpga_c11_ops', 'fpga_c22_ops'], 'Ops': [cx5_c11_ops, cx5_c22_ops, fpga_c11_ops, fpga_c22_ops]}
    df = pd.DataFrame(data=data_ops)
    # print(df)
    # data_ops = [[cx5_c11_ops, cx5_c22_ops, fpga_c11_ops, fpga_c22_ops]]
    # df = pd.DataFrame(data_ops)
    # df.columns =['cx5_c11', 'cx5_c22', 'fpga_c11', 'fpga_c22']

    fig = plot_ops_summary(df)

    fig.update_layout(
            title="Memcached (All Instances) - Operations per Second - Yeti (CX5 and FPGA)",
            xaxis_title="<b>NIC TYPE</b>",
            yaxis_title="<b>Ops</b>"
            # yaxis={'tickformat': ',d'}
        )

    filename_plot = DATAPATH_SUMMARY + "ops_summary.html"
    plotly.offline.plot(fig, filename=filename_plot)


load_summary()