from poc.plugin import plugin
from poc.powerqueue import pq
from poc.db import db

# Pulls messages from preprocess.crawl and expects the FILENAME field.
#
# This plugin essentially provides a passthrough for the preprocess.crawl
# queue.  It generates a RecordStore entry for each incoming message and
# then passes the message on. 

class FileSystem(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(FileSystem, self).__init__()

    def init(self):
        self.setOutputQueueName('localhost', 'preprocess.annotate')
        self.setRecordStoreHost('localhost')

    def runloop(self):
        in_queue = pq.ConsumerQueue('localhost', 'preprocess.crawl')
        in_queue.register_callback(self.execute)

        print "Launching reader with FileSystem plugin..."
        in_queue.start_waiting()
        
    def execute(self, msg):
        record = db.Record()
        record.filename = msg.filename
        
        rs = self.getRecordStore()
        if not rs.record_exists(record):
            rid = rs.store(record)

        # Create a new message for all RSS feeds.
        msg = pq.Message()
        msg.rid = rid

        # Send the message
        outq = self.getOutputQueue()
        outq.send(msg)
