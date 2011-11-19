import pq, sys

# This script is both a demo of the queue and a tool for sending
#   messages to arbitrary queues.  The first parameter passed to
#   the script will be interpreted as the queue name and the second
#   will be parsed as a chain of fields for the Message that's
#   generated for the queue.  The message chain is provided in the form:
#      [key]=[value];[key]=[value]

# Create a queue that will receive events as needed.
#   The queue lives at localhost and is called 'pending.preprocess'
#   The queue name needs to be shared between the consumer and producer.
queue = pq.ProducerQueue('localhost', sys.argv[1])

# Generate a message from the command line.
message = pq.Message()
params = [param.split('=') for param in sys.argv[2].split(';')]
for key, value in params:
    message.__dict__[key] = value

queue.send(message)
queue.__del__()