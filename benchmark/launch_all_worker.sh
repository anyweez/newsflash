#!/bin/bash
# Abort if anything returns an error.
set -o errexit

# Preconditions - git checkout exists in ~/newsflash
#               - the MySQL server has no image table.
#               - the photos exist on the filesystem 

cd ~/newsflash

echo "nuking logs/ directory..."
rm -rf logs
mkdir logs
# Kill anything that's actively running.
echo "killing any running newsflash python instances..."
JOBS=$(ps aux | grep 'python launch.py' | grep -v grep | awk '{ print $2}')
kill ${JOBS} || true # possible that this line will fail

# Set the config file's local ip for Cassandra to the machine's local ip.
IP_ADDR=$(ip addr | grep eth0 | grep inet | awk '{print $2}' | cut -d / -f 1)
echo "Setting matrix_host to ${IP_ADDR}"
sed s/^matrix_host.*$/matrix_host\ =\ ${IP_ADDR}/ --in-place config.ini

# Launch all of the things in the background
echo "Launching a pile of newsflash instances..."
python launch.py similarity ImageSimilarity > logs/ImageSimilarity.log.1 &
python launch.py similarity ImageSimilarity > logs/ImageSimilarity.log.2 &
python launch.py annotator ImageAnnotator > logs/ImageAnnotator.log.1 &
python launch.py annotator ImageAnnotator > logs/ImageAnnotator.log.2 &
python launch.py webapi CompletionNotifier > logs/CompletionNotifier.log.1 &
python launch.py reader FileSystem > logs/FileSystem.log.1 &

echo "Now fire off benchmarks/launch_all_rabbit.sh on the RabbitMQ node."

# Unused modules:
#    webapi WebAPI
#    similarity WordIncidence
#    annotator ANNOTATE
#    reader LoadFeeds
#    reader RSS
