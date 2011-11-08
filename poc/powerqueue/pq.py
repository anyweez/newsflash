import pika, cPickle

# Base class for the two queues.  Not intended to be instantiated
#   directly.
class PowerQueue(object):
    def __init__(self, host, queue_name):
        self._conn = pika.BlockingConnection(pika.ConnectionParameters(host=host))
        self._chan = self._conn.channel()
        
        self.queue_name = queue_name
        self._chan.queue_declare(queue=queue_name, durable=True)
        self._chan.basic_qos(prefetch_count = 1)
        
    def __del__(self):
        self._conn.close()

    def getChannel(self):
        return self._chan

# An object that sends messages to a particular queue.  Pretty
#   straightforward.
class ProducerQueue(PowerQueue):
    def __init__(self, host, queue_name):
        super(ProducerQueue, self).__init__(host, queue_name)

    def __del__(self):
        super(ProducerQueue, self).__del__()

    def send(self, msg):
        self.getChannel().basic_publish(
            exchange='', 
            routing_key=self.queue_name, 
            body=cPickle.dumps(msg),
            properties=pika.BasicProperties(
                # Makes messages persistent.
                delivery_mode = 2,
            )
        )

# An object that pulls messages from a queue.  The start_waiting
#   method will block until a message arrives, and will then call
#   the specified callback function.
class ConsumerQueue(PowerQueue):
    def __init__(self, host, queue_name):
        super(ConsumerQueue, self).__init__(host, queue_name)
        self.getChannel().basic_consume(self._callback, queue=queue_name)
        
    def __del__(self):
        super(ConsumerQueue, self).__del__()

    def register_callback(self, func):
        self._callback = func
        
    # Start receiving events and call the callback function
    #   once a new event arrives.
    def start_waiting(self):
        if self._callback is not None:
            self.getChannel().start_consuming()
        else:
            raise Exception('You must register a callback before receiving events.')
    
    def _ack(self, delivery_tag):
        self.getChannel().basic_ack(delivery_tag = delivery_tag)
    
    def _callback(self, ch, method, properties, body):
        # Call the function with the message data
        self._callback(cPickle.loads(body))
        # Acknowledge that the task completed successfully/
        #   This will remove the task from the RMQ queue.
        self._ack(method.delivery_tag)    
        
class Message(object):
    def __init__(self):
        pass