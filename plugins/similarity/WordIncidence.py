import numpy
from poc.plugin import plugin
from poc.powerqueue import pq
from collections import defaultdict

class WordIncidence(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(WordIncidence, self).__init__()

    def init(self):
        self.setOutputQueue('completed')
        self.setInputQueue('similarity')
            
    def execute(self, msg):
        secondary = int(msg.secondary_min)
        mstore = self.getMatrixStore()
        while secondary < (int(msg.secondary_max) + 1):
            print "Word Incidence: processing incidence between rid %s and rid %s" % (msg.first, msg.second)
            rstore = self.getRecordStore()
            r1 = rstore.get(msg.primary)
            r2 = rstore.get(secondary)
            
            if hasattr(r2, 'tfidf'):
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
                mstore.set_val(x=msg.first, y=msg.second, val=similarity)
            else:
                # Otherwise the data hasnt' been set yet and we should bail for now.
                self.defer(msg)
                return
        outq = self.getOutputQueue()    
        outq.send(msg)

    def runloop(self):
        in_queue = self.getInputQueue()
        in_queue.register_callback(self.execute)
        print "Launching similarity..."
        in_queue.start_waiting()
