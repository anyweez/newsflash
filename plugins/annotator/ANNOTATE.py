import numpy, logging, sys
from gensim import corpora, models
from poc.plugin import plugin
from poc.powerqueue import pq
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
    
class ANNOTATE(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(ANNOTATE, self).__init__()
        
    def init(self):
        self.setOutputQueue('similarity')
        self.setInputQueue('annotate')

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
        record=rstore.get(rid)  #open record from rstore with rid      
        dictionary = corpora.Dictionary.load('/tmp/dictionary.dict')  
        corpus = corpora.MmCorpus('/tmp/newsflash.mm')
        tfidf = models.TfidfModel(corpus) # step 1 -- initialize a model
        #record.full_text = "cain romney gingrich bachmann"
        if len(record.full_text)==0:
                record.full_text="This record is empty"
        #        sys.exit("THERE IS NO DATA AVAILABLE! ")
        document_analyzed = dictionary.doc2bow(record.full_text.lower().split())
        record.tfidf = tfidf[document_analyzed]
        print record.tfidf
        rstore.update(rid, record)
        self.send_messages(rid)
        
    def runloop(self):
        in_queue = self.getInputQueue()
        in_queue.register_callback(self.execute)
        print "Launching annotator..."
        in_queue.start_waiting()

