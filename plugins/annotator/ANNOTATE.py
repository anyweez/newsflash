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
        #title, publication date, source, full text
        #   open("filefake.csv", "wb", message)
            pqueue.send(message)
        #push message to preprocess.annotate
    
    def execute(self, msg):
        print "Annotating: %s" % (msg.rid)
        
        rstore = self.getRecordStore()
# calculations = [mean, count]
#        rstore = db.RecordStore("localhost")

        rid=msg.rid  #open message get id
        record=rstore.get(rid)  #open record from rstore with rid
        
        record.count=len(record.full_text)
    
#   for i in calculations:    #make all needed calculations and append them to record
#       record.i=calculations(record.data,i)  
        rstore.update(rid, record)
        self.send_messages(rid)
        
