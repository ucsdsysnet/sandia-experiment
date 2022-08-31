#!/bin/bash

# https://www.systutorials.com/docs/linux/man/3-sockperf/
# https://docs.nvidia.com/networking/pages/viewpage.action?pageId=43720014

sudo apt install perl make automake autoconf m4 libtool-bin g++

cd $HOME/sw
git clone https://github.com/Mellanox/sockperf.git 
cd $HOME/sw/sockperf/
./autogen.sh
./configure
make
sudo make install