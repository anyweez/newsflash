#!/bin/bash

# Abort on errors
set -e

# get to a known path
cd ~/newsflash/

# nuke the logs
echo "nuking logs/ directory..."
rm -rf logs
mkdir logs

# Drop table from MySQL.
echo "dropping image table"
echo "DROP TABLE IF EXISTS image" | mysql -u newsflash --password=rDZtewnGUULH2Jjs newsflash

# Purge the queues by deleting them and creating empty ones.
# Since deleting a nonexistent queue will error, we ensure that all queues
# exist before deleting them (since amq-declare-queue IS idempotent)
# This is somewhat ridiculous.
echo "purging AMQP queues"
for QUEUE in preprocess.crawl preprocess.annotate preprocess.similarity preprocess.completed ; do
	amqp-declare-queue -d -q ${QUEUE}
	amqp-delete-queue -q ${QUEUE}
	amqp-declare-queue -d -q ${QUEUE}
done

# Start the queue length watcher in the background
echo "Starting queue length watcher..."
python benchmark/get_queue_length.py preprocess.crawl preprocess.annotate preprocess.similarity preprocess.completed > logs/QueueLengthMonitor.log &

sleep 2s

echo "Seeding queues with filesystem paths."
python pump_fs_events.py preprocess.crawl data/photos
