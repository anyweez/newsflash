import numpy
from poc.plugin import plugin
from poc.powerqueue import pq

class ANNOTATE(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(ANNOTATE, self).__init__()
        
    def init(self):
        self.setOutputQueueName('localhost', 'preprocess.similarity')
        self.setRecordStoreHost('localhost')
        
    def send_messages(self, rid):
        message=pq.Message()
        message.first = rid
        pqueue = self.getOutputQueue()
        for i in range(1,rid):
            message.second = i #i goest to rid - 1
            pqueue.send(message) #push messages to preprocess.similarity
    
    def execute(self, msg):
        print "Annotating: %s" % (msg.rid)
        
        rstore = self.getRecordStore()
        rid=msg.rid  #open message get id
#	if (record_loaded(rid)):
        record=rstore.get(rid)  #open record from rstore with rid        
        
        record.count=len(record.full_text)
        rstore.update(rid, record)
        self.send_messages(rid)
        
    def runloop(self):
        in_queue = pq.ConsumerQueue('localhost', 'preprocess.annotate')
        in_queue.register_callback(self.execute)
        print "Launching annotator..."
        in_queue.start_waiting()

