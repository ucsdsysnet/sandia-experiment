#!/bin/bash

cd "$(dirname "$0")"

for i in {36..1060}; do
    test=$(echo $i%256 | bc)
    echo $test
done