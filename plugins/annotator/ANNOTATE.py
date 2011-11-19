import numpy
from poc.plugin import plugin

class message():
    pass

class ANNOTATE(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(ANNOTATE, self).__init__()
        
    def init(self):
        self.setOutputQueueName('localhost', 'preprocess.similarity')
        self.setRecordStoreHost('localhost')
        
    def send_messages(self, rid):
        message.first = rid
        for i in rid - 1:
            message.second = i #i goest to rid - 1
        #title, publication date, source, full text
        #   open("filefake.csv", "wb", message)
        pqueue = self.getOutputQueue()
        pqueue.send(message)
        #push message to preprocess.annotate
    
    def execute(self, msg):
        print "Annotating: %s" % (msg.url)

        rstore = self.getRecordStore()
# calculations = [mean, count]
#        rstore = db.RecordStore("localhost")

        rid=msg.rid  #open message get id
        record=rstore.get(rid)  #open record from rstore with rid
        
        record.count=len(record.full_text)
    
#   for i in calculations:    #make all needed calculations and append them to record
#       record.i=calculations(record.data,i)  
        rstore.update(record)
        self.send_messages(rid)
        
