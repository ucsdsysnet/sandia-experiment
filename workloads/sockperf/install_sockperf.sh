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

# under-load (ul)      Run sockperf client for latency under load test.
# ping-pong (pp)       Run sockperf client for latency test in ping pong mode.
# playback (pb)        Run sockperf client for latency test using playback of predefined traffic, based on timeline and message size.
# throughput (tp)      Run sockperf client for one way throughput test.
# server (sr)          Run sockperf as a server.