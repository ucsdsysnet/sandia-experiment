import pandas as pd
import plotly
import plotly.graph_objects as go

BASE_PATH = "/home/dathapathu/experiments/"

DATAPATH_SUMMARY = BASE_PATH+"data-summary/"

cx5_c11_path = BASE_PATH + "data-summary/" + "summary-c11-cx5.csv"
cx5_c22_path = BASE_PATH + "data-summary/" + "summary-c22-cx5.csv"
fpga_c11_path = BASE_PATH + "data-summary/" + "summary-c11-fpga.csv"
fpga_c22_path = BASE_PATH + "data-summary/" + "summary-c22-fpga.csv"

def plot_summary(fig, df_summary, identifier):
    fig.add_trace(
                go.Scatter(x=df_summary["instance_id"], y=df_summary["p50"], name=identifier + "-p50", mode='lines', text=df_summary["p50"])
            )
    fig.add_trace(
                go.Scatter(x=df_summary["instance_id"], y=df_summary["p99"], name=identifier + "-p99", mode='lines', text=df_summary["p99"])
            )
    fig.add_trace(
                go.Scatter(x=df_summary["instance_id"], y=df_summary["p99_9"], name=identifier + "-p99_9", mode='lines', text=df_summary["p99_9"])
            )
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

    fig = go.Figure()
    fig = plot_summary(fig, cx5_c11, "cx5_c11")
    fig = plot_summary(fig, cx5_c22, "cx5_c22")
    fig = plot_summary(fig, fpga_c11, "fpga_c11")
    fig = plot_summary(fig, fpga_c22, "fpga_c22")

    fig.update_layout(
            title="p50, p99, p99.9 Percentile Latency - Yeti (CX5 and FPGA)",
            xaxis_title="<b>Client Instance ID</b>",
            yaxis_title="<b>Latency (milliseconds)</b>"
            # yaxis={'tickformat': ',d'}
        )

    filename_plot = DATAPATH_SUMMARY + "percentile_latency_summary.html"
    plotly.offline.plot(fig, filename=filename_plot)

load_summary()