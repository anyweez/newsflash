from powerqueue import pq
import time 

def call_me(message):
    print "Received message: %s" % (message,)
    time.sleep(len(message))

# Create a queue that will receive events as needed.
#   The queue lives at localhost and is called 'pending.preprocess'
#   The queue name needs to be shared between the consumer and producer.
queue = pq.ConsumerQueue('localhost', 'pending.preprocess')

# The function that should be called when a message arrives.
queue.register_callback(call_me)
# Let's get this party started.
print "Waiting for messages..."
queue.start_waiting()