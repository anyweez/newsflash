#!/bin/bash

# Abort on errors
set -e

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

echo "Good to go.  Start benchmark/launch_all_worker.sh on all the nodes."
