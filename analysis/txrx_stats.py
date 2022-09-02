import sys
sys.path.insert(0, 'workloads')
import analyzer as az 
import constant as c 
import pandas as pd

def populate_analyzer(analyzer):
    analyzer.txrx_logs
    return analyzer

all_analysers = az.get_experiment_analysers(f"*{sys.argv[1]}*", sys.argv[2], sys.argv[3])
for analyser_id in all_analysers:
    print("~~~~~",analyser_id, "~~~~~")
    analyzer = populate_analyzer(all_analysers[analyser_id])
    
    analyzer.df_client_txrx_stats['sent_tx_packets'] = analyzer.df_client_txrx_stats['end_tx'] - analyzer.df_client_txrx_stats['start_tx']
    analyzer.df_client_txrx_stats['sent_rx_packets'] = analyzer.df_client_txrx_stats['end_rx'] - analyzer.df_client_txrx_stats['start_rx']
    print(analyzer.df_client_txrx_stats.head(35))