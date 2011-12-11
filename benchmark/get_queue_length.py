import pika, sys, time

## This script continuously polls a RabbitMQ instance and fetches the
## length of various queues.  The queue names should be specified as
## parameters on the command line.
##
## Example call:
##   python get_queue_length.py preprocess.crawl preprocess.annotate

# The poll frequency in seconds.
poll_frequency = .5

# Get the name of all queues from the command line
queues = []
for queue_name in sys.argv[1:]:
	queues.append(queue_name)

conn = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
chan = conn.channel()

print '\t'.join(['timestamp'] + queues)
while True:
	counts = [str(time.time()),]
	for q in queues:
		m = chan.queue_declare(queue=q, passive=True)
		counts.append(str(m.method.message_count))
		
	print '\t'.join(counts)
	sys.stdout.flush()
	time.sleep(poll_frequency)
