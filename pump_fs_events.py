import sys, os
from poc.powerqueue import pq

# Adds a message containing a filename to the specified queue.
if len(sys.argv) is not 3:
    print "Specify a queue to pump to and a directory to pull filenames from."
    sys.exit(1)

pqueue = pq.ProducerQueue('localhost', sys.argv[1])

files = os.listdir(sys.argv[2])

for i, f in enumerate(files):
    if i < 2000:
        msg = pq.Message()
        msg.filename = f
        pqueue.send(msg)
    else:
        break

print 'Generated messages for %d files.' % len(files)
