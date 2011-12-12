import numpy
from poc.plugin import plugin
from poc.powerqueue import pq
from collections import defaultdict

class WordIncidence(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(WordIncidence, self).__init__()

    def init(self):
        self.setInputQueue('similarity')

    def send_back_messages(self, rid):
        message=pq.Message()
        message.first = rid
        pqueue = self.getOutputQueue()
        for i in range(1,rid):
            message.second = i #i goest to rid - 1
            pqueue.send(message) #push messages to preprocess.similarity
            
    def execute(self, msg):
        print "Word Incidence: processing incidence between rid %s and rid %s" % (msg.first, msg.second)
        rstore = self.getRecordStore()
        r1 = rstore.get(msg.first)
        r2 = rstore.get(msg.second)
        if len(r1)==0:
            
 #       print "THIS IS THE MAIN"
 #       print r1.full_text
 #       print "THIS IS THE SECOND"
 #       print r2.full_text

        # Known fields: 'author', 'count', 'full_text', 'link', 'pubDate', 'summary', 'title'
      #  print "record", msg.first, ":", dir(r1)

        # Do something with the fields to compute a float representing similarity
        vec1 = r1.tfidf
        vec2 = r2.tfidf
        k1,v1 = zip(*vec1)
        k2,v2 = zip(*vec2)
        vec1d = defaultdict( list )
        for v, k in vec1:
            vec1d[v].append(k)
        vec2d = defaultdict( list )
        for v, k in vec2:
            vec2d[v].append(k)
        
        intersect = filter(lambda key: key in k2, k1)
        not_intersect2 = filter(lambda key: key not in k2, k1)
        not_intersect1 = filter(lambda key: key not in k1, k2)
        not_intersect = not_intersect1+not_intersect2
        values1 = []
        values2 = []
        for i in intersect+not_intersect:
            if (i in vec1d):
                values1.append(vec1d[i][0])
            else:
                values1.append(0)
            if (i in vec2d):
                values2.append(vec2d[i][0])
            else:
                values2.append(0)
        similarity = numpy.dot(values1,values2)        
        print similarity
        mstore = self.getMatrixStore()
        mstore.set_val(x=msg.first, y=msg.second, val=similarity)

    def runloop(self):
        in_queue = self.getInputQueue()
        in_queue.register_callback(self.execute)
        print "Launching similarity..."
        in_queue.start_waiting()
