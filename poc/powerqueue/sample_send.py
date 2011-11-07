from powerqueue import pq
import sys

# Create a queue that will receive events as needed.
#   The queue lives at localhost and is called 'pending.preprocess'
#   The queue name needs to be shared between the consumer and producer.
queue = pq.ProducerQueue('localhost', 'pending.preprocess')

queue.send(sys.argv[1])