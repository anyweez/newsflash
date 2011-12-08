import numpy
import PIL.Image as Image
from poc.plugin import plugin
from poc.powerqueue import pq

class ImageAnnotator(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(ImageAnnotator, self).__init__()
        
    def init(self):
        self.setOutputQueueName('localhost', 'preprocess.similarity')
        self.setInputQueueName('localhost', 'preprocess.annotate')
        self.setRecordStoreHost('localhost')
        
    def send_messages(self, rid):
        message=pq.Message()
        message.first = rid
        pqueue = self.getOutputQueue()
        
        for i in xrange(0, rid):
            message.second = i 
            pqueue.send(message)
    
    def execute(self, msg):
        print "Annotating: %s" % (msg.rid)
        
        rstore = self.getRecordStore()
        record = rstore.get(msg.rid)  #open record from rstore with rid

        img = Image.open("/home/luke/Desktop/flickr-pull/photos/%s" % record.filename)
        hist = img.histogram()
        
        record.r_hist = hist[:256]
        record.g_hist = hist[256:512]
        record.b_hist = hist[512:]
        
        rstore.update(msg.rid, record)
        self.send_messages(msg.rid)
        
    def runloop(self):
        in_queue = self.getInputQueue()
        in_queue.register_callback(self.execute)
        print "Launching ImageAnnotator..."
        in_queue.start_waiting()

