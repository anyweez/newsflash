#!/bin/bash

sudo add-apt-repository ppa:cassandra-ubuntu/stable
sudo apt-get update
sudo apt-get -y install python-mysqldb python-feedparser python-gevent python-beautifulsoup python-imaging python-numpy python-pip build-essential git-core cassandra
sudo pip install pika==0.9.5
sudo pip install pycassa

cd newsflash
wget http://10.240.107.17/photos.tar.gz
mkdir data
mv photos.tar.gz data/
cd data
tar zfx photos.tar.gz
