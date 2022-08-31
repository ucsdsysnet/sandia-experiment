#!/bin/bash

sudo apt-get install -y apache2
sudo service apache2 stop

# Download usatoday homepage
cd /var/www/html && sudo wget --no-check-certificate --adjust-extension --span-hosts --convert-links --backup-converted --page-requisites www.usatoday.com

# http://128.110.218.254/www.usatoday.com/ 

# Download DASH dataset (http://ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/15sec/)
# cd /var/www/html && sudo wget -r ftp://ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/15sec/
# sudo mv ftp.itec.aau.at/datasets/DASHDataset2014/BigBuckBunny/15sec/* .
