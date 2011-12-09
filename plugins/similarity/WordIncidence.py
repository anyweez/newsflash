from poc.plugin import plugin
from poc.powerqueue import pq

class WordIncidence(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(WordIncidence, self).__init__()

    def init(self):
        pass

    def execute(self, msg):
        print "Word Incidence: processing incidence between rid %s and rid %s" % (msg.first, msg.second)
        rstore = self.getRecordStore()
        r1 = rstore.get(msg.first)
        r2 = rstore.get(msg.second)

        # Known fields: 'author', 'count', 'full_text', 'link', 'pubDate', 'summary', 'title'
        print "record", msg.first, ":", dir(r1)
        print r1.count

        # Do something with the fields to compute a float representing similarity
        similarity = 0.5

        mstore = self.getMatrixStore()
        mstore.set_val(x=msg.first, y=msg.second, value=similarity)

    def runloop(self):
        in_queue = pq.ConsumerQueue('localhost', 'preprocess.similarity')
        in_queue.register_callback(self.execute)
        print "Launching similarity..."
        in_queue.start_waiting()
