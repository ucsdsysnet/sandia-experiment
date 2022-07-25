import glob
import os
import tarfile

DATAPATH_RAW="/home/dathapathu/experiments/data-tmp/"
DATAPATH_PROCESSED="/home/dathapathu/experiments/data-processed/"

def load_experiments(experiment_name_pattern):
    num_local_files = 0
    local_filepath = glob.glob(os.path.join(DATAPATH_RAW,experiment_name_pattern +'.tar'))
    print(local_filepath[0])
    if os.path.isfile(local_filepath[0]) and len(os.listdir(DATAPATH_PROCESSED)) == 0:
        print("Extracting tar...")
        my_tar = tarfile.open(local_filepath[0])
        my_tar.extractall(DATAPATH_PROCESSED)
        my_tar.close()
    
load_experiments("*25-07-2022_095308*")