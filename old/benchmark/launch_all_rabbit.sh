#!/bin/bash

# Abort on errors
set -e

# get to a known path
cd ~/newsflash/

# nuke the logs
echo "nuking logs/ directory..."
rm -rf logs
mkdir logs

# Start the queue length watcher in the background
echo "Starting queue length watcher..."
python benchmark/get_queue_length_rabbitmqctl.py > logs/QueueLengthMonitor.log &

sleep 2s

echo "Seeding queues with filesystem paths."
python pump_fs_events.py preprocess.crawl data/photos
