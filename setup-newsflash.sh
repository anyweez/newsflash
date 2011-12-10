#!/bin/bash

sudo apt-get -y install python-mysqldb python-feedparser python-gevent python-beautifulsoup python-imaging python-numpy python-pip build-essential git-core
sudo pip install pika==0.9.5
sudo pip install pycassa
sudo add-apt-repository cassandra-ubuntu/stable
sudo apt-get update
sudo apt-get -y install cassandra

git clone git://github.com/luke-segars/newsflash
