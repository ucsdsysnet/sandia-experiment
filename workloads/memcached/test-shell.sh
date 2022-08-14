#!/bin/bash

list="$(find /tmp/data-tmp/ -type f ! -name \*.tar -delete)"
echo $list