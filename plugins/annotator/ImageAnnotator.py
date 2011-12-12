import numpy, math
import PIL.Image as Image
from poc.plugin import plugin
from poc.powerqueue import pq

class ImageAnnotator(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(ImageAnnotator, self).__init__()
        
    def init(self):
        self.setOutputQueue('similarity')
        self.setInputQueue('annotate')
        
    def send_messages(self, rid):
        message=pq.Message()
        message.primary = rid
        pqueue = self.getOutputQueue()
        
        # We should be generating similarity_batch_count messages, each
        #   equal in size.  This value can be changed in config.ini.
        batch_count = int(self.getParam('similarity_batch_count'))
        size = int(math.ceil(rid / batch_count))
        
        if size < 1:
            size = 1
            message.secondary_min = 1
            message.secondary_max = rid - 1
            pqueue.send(message)
        else: 
            for i in xrange(0, batch_count):
                message.secondary_min = 1 + (i * size)
                if ((i + 1) * size) < rid:
                    message.secondary_max = (i + 1) * size
                else:
                    message.secondary_max = rid - 1
                pqueue.send(message)
    
    def execute(self, msg):
        print "Annotating: %s" % (msg.rid)
        
        rstore = self.getRecordStore()
        record = rstore.get(msg.rid)  #open record from rstore with rid

        img = Image.open("data/photos/%s" % record.filename)
        hist = img.histogram()
        
        # Get histograms for each color channel (assumed
        #   to be three).
        pixelcount = float(img.size[0] * img.size[1])
        record.r_hist = [x / pixelcount for x in hist[:256]]
        record.g_hist = [x / pixelcount for x in hist[256:512]]
        record.b_hist = [x / pixelcount for x in hist[512:]]
        
        rstore.update(int(msg.rid), record)
        self.send_messages(msg.rid)
        
    def runloop(self):
        in_queue = self.getInputQueue()
        in_queue.register_callback(self.execute)
        print "Launching ImageAnnotator..."
        in_queue.start_waiting()

