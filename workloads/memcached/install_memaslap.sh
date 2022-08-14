#!/bin/bash

wget https://launchpad.net/libmemcached/1.0/1.0.18/+download/libmemcached-1.0.18.tar.gz
tar -xvf libmemcached-1.0.18.tar.gz

# Install libevent needed for memaslap
sudo apt-get install libevent-dev

sudo apt-get install autogen libtool shtool

# sudo ln -sf /usr/bin/aclocal /usr/bin/aclocal-1.13
# sudo ln -sf /usr/bin/automake /usr/bin/automake-1.13

cd libmemcached-1.0.18
 
 
# Edit Makefile by adding LDFLAGS "-L/lib64 -lpthread"
# https://bugs.launchpad.net/libmemcached/+bug/1562677
### diff of Makefile
# -LDFLAGS =
# +LDFLAGS = -L/lib64 -lpthread 
###

vim Makefile
 
# After running ./configure step make sure configure log says:
# checking test for a working libevent... yes
./configure --enable-memaslap

sudo automake --add-missing
 
sudo make install
 
# Run memaslap 
./clients/memaslap -s 127.0.0.1:11211 -t 20s