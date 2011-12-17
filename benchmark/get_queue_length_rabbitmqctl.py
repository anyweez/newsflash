#!/usr/bin/env python
import subprocess
import time
import sys

# Since it appears that we get no useful data from pika, we'll try calling
# rabbitmqctl from the shell.  Often.

queues_of_interest = ["preprocess.crawl",
        "preprocess.annotate",
        "preprocess.similarity",
        "preprocess.completed"]

header = ["timestamp"]
header.extend(queues_of_interest)

print "\t".join(header)

while True:
    text = subprocess.check_output(["sudo", "rabbitmqctl", "list_queues"])
    timestamp = time.time()
    thissample = {}
    fields = text.split()
    for queue in queues_of_interest:
        thissample[queue] = fields[fields.index(queue) + 1]
    outline_fields = [str(timestamp)]
    outline_fields.extend(map(lambda x: thissample[x], queues_of_interest))
    print "\t".join(outline_fields)
    sys.stdout.flush()
    time.sleep(1)
