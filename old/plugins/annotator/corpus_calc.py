from poc.db import db
from gensim import corpora, models
import logging, cPickle, numpy, sys
import scipy.sparse as sparse
from collections import defaultdict
import pickle
logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

class corpus_calc(object):
    def __init__(self):
        # Call your own constructor
        self.database = db.RecordStore

    def mycorpus(self, document_base, dictionary):
        for line in document_base:
# assume there's one document per line, tokens separated by whitespace
            yield dictionary.doc2bow(line.lower().split())
            
    def run(self):
        rstore = self.database("localhost")
        print "Updating corpus..." 
        first_rid = rstore.execute("SELECT rid FROM records ORDER BY rid ASC LIMIT 1", [])
        last_rid = rstore.execute("SELECT rid FROM records ORDER BY rid DESC LIMIT 1", [])
        print first_rid
        print last_rid
        document_objects = rstore.getrange(list(first_rid)[0][0], list(last_rid)[0][0])  #open record from rstore with rid
        stoplist = set('for a of the and to in'.split())
        documents = [document.full_text for document in document_objects]
        dictionary = corpora.Dictionary(line.lower().split() for line in documents)
        stop_ids = [dictionary.token2id[stopword] for stopword in stoplist
                    if stopword in dictionary.token2id]
        once_ids = [tokenid for tokenid, docfreq in dictionary.dfs.iteritems() if docfreq == 1]
        dictionary.filter_tokens(stop_ids + once_ids) # remove stop words and words that appear only once
        dictionary.compactify() # remove gaps in id sequence after words that were removed
        dictionary.save("/tmp/dictionary.dict")  # store the dictionary, for future reference
        corpus = self.mycorpus(documents, dictionary)
        corpora.MmCorpus.serialize('/tmp/newsflash.mm', corpus) # store to disk, for later use
        print "New corpus calculated!"
                
corpusa = corpus_calc()
corpusa.run()