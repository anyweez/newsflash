import PIL.Image as Image
from poc.plugin import plugin
from poc.powerqueue import pq

class ImageSimilarity(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(ImageSimilarity, self).__init__()

    def init(self):
        self.setRecordStoreHost('localhost')
        self.setMatrixStoreHost('localhost')

    def execute(self, msg):
        print "Comparing histograms of rid %s and rid %s" % (msg.first, msg.second)
        rstore = self.getRecordStore()
        r1 = rstore.get(msg.first)
        r2 = rstore.get(msg.second)

        image1 = Image.open('photos/%s' % r1.filename)
        image2 = Image.open('photos/%s' % r2.filename)
    
        # Get histograms for each color channel (assumed
        #   to be three).  Both images.
        h1 = image1.histogram()
        pixels1 = float(image1.size[0] * image1.size[1])
        r1 = [x / pixels1 for x in h1[:256]]
        g1 = [x / pixels1 for x in h1[256:512]]
        b1 = [x / pixels1 for x in h1[512:]]
    
        h2 = image2.histogram()
        pixels2 = float(image2.size[0] * image2.size[1])
        r2 = [x / pixels2 for x in h2[:256]]
        g2 = [x / pixels2 for x in h2[256:512]]
        b2 = [x / pixels2 for x in h2[512:]]
    
        # Difference in individual histogram values seems
        #   to work pretty well.
        r_delt = sum([abs(a - b) for a, b in zip(r1, r2)])
        g_delt = sum([abs(a - b) for a, b in zip(g1, g2)])
        b_delt = sum([abs(a - b) for a, b in zip(b1, b2)])

        mstore = self.getMatrixStore()
        # In my tests it seems like 2 is the largest delta
        #   value that can be generated for a single channel.
        #   Since there are three channels, the max value is
        #   6.  Invert and normalize to fall between the range
        #   [0, 1] where higher = more similar.
        similarity = (6 - (r_delt + g_delt + b_delt)) / 6
        mstore.set_val(x=msg.first, y=msg.second, value=similarity)

    def runloop(self):
        in_queue = pq.ConsumerQueue('localhost', 'preprocess.similarity')
        in_queue.register_callback(self.execute)
        print "Launching similarity..."
        in_queue.start_waiting()
