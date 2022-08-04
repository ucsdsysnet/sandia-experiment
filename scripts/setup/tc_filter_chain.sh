#!/bin/bash

cd "$(dirname "$0")"

sudo tc filter add dev ens4 egress prio 1 handle 8: protocol ip u32 divisor 256

# Direct traffic in root hashtable 800: to hash table 2: we created earlier
sudo tc filter add dev ens4 egress protocol ip prio 1 \
        u32 ht 800:: \
        link 8: hashkey mask 0x000000ff at 16 \
        match ip dst 10.10.20.0/24 

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000065 0x000000ff at 16 \
                      match ip dst 10.10.20.101 \
                      action skbedit queue_mapping 1

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000066 0x000000ff at 16 \
                      match ip dst 10.10.20.102 \
                      action skbedit queue_mapping 2

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000067 0x000000ff at 16 \
                      match ip dst 10.10.20.103 \
                      action skbedit queue_mapping 3

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000068 0x000000ff at 16 \
                      match ip dst 10.10.20.104 \
                      action skbedit queue_mapping 4

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000069 0x000000ff at 16 \
                      match ip dst 10.10.20.105 \
                      action skbedit queue_mapping 5

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000006a 0x000000ff at 16 \
                      match ip dst 10.10.20.106 \
                      action skbedit queue_mapping 6

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000006b 0x000000ff at 16 \
                      match ip dst 10.10.20.107 \
                      action skbedit queue_mapping 7

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000006c 0x000000ff at 16 \
                      match ip dst 10.10.20.108 \
                      action skbedit queue_mapping 8

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000006d 0x000000ff at 16 \
                      match ip dst 10.10.20.109 \
                      action skbedit queue_mapping 9

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000006e 0x000000ff at 16 \
                      match ip dst 10.10.20.110 \
                      action skbedit queue_mapping 10

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000006f 0x000000ff at 16 \
                      match ip dst 10.10.20.111 \
                      action skbedit queue_mapping 11

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000070 0x000000ff at 16 \
                      match ip dst 10.10.20.112 \
                      action skbedit queue_mapping 12


sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000071 0x000000ff at 16 \
                      match ip dst 10.10.20.113 \
                      action skbedit queue_mapping 13

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000072 0x000000ff at 16 \
                      match ip dst 10.10.20.114 \
                      action skbedit queue_mapping 14

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000073 0x000000ff at 16 \
                      match ip dst 10.10.20.115 \
                      action skbedit queue_mapping 15

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000074 0x000000ff at 16 \
                      match ip dst 10.10.20.116 \
                      action skbedit queue_mapping 16

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000075 0x000000ff at 16 \
                      match ip dst 10.10.20.117 \
                      action skbedit queue_mapping 17

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000076 0x000000ff at 16 \
                      match ip dst 10.10.20.118 \
                      action skbedit queue_mapping 18

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000077 0x000000ff at 16 \
                      match ip dst 10.10.20.119 \
                      action skbedit queue_mapping 19

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000078 0x000000ff at 16 \
                      match ip dst 10.10.20.120 \
                      action skbedit queue_mapping 20

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000079 0x000000ff at 16 \
                      match ip dst 10.10.20.121 \
                      action skbedit queue_mapping 21

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000007a 0x000000ff at 16 \
                      match ip dst 10.10.20.122 \
                      action skbedit queue_mapping 22

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000007b 0x000000ff at 16 \
                      match ip dst 10.10.20.123 \
                      action skbedit queue_mapping 23

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000007c 0x000000ff at 16 \
                      match ip dst 10.10.20.124 \
                      action skbedit queue_mapping 24

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000007d 0x000000ff at 16 \
                      match ip dst 10.10.20.125 \
                      action skbedit queue_mapping 25

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000007e 0x000000ff at 16 \
                      match ip dst 10.10.20.126 \
                      action skbedit queue_mapping 26

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x0000007f 0x000000ff at 16 \
                      match ip dst 10.10.20.127 \
                      action skbedit queue_mapping 27

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000080 0x000000ff at 16 \
                      match ip dst 10.10.20.128 \
                      action skbedit queue_mapping 28

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000081 0x000000ff at 16 \
                      match ip dst 10.10.20.129 \
                      action skbedit queue_mapping 29

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000082 0x000000ff at 16 \
                      match ip dst 10.10.20.130 \
                      action skbedit queue_mapping 30

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000083 0x000000ff at 16 \
                      match ip dst 10.10.20.131 \
                      action skbedit queue_mapping 31

sudo tc filter add dev ens4 egress protocol ip prio 1 u32 \
                      ht 8: sample u32 0x00000084 0x000000ff at 16 \
                      match ip dst 10.10.20.132 \
                      action skbedit queue_mapping 32