import feedparser, urllib2, httplib#, gevent

#from gevent import monkey
from poc.plugin import plugin
from poc.db import db
from poc.fulltext_parser import articletxt
from poc.powerqueue import pq
from urllib2 import HTTPError, URLError
from BeautifulSoup import BeautifulSoup

class RSS(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(RSS, self).__init__()
#        monkey.patch_all()
        
    def init(self):
        self.setInputQueue('crawl')
        self.setOutputQueue('annotate')
        
    def process_record(self, record, outq):
        print '  Fetching url %s' % record.link
        finished = False
        added = False
        attempts = 0
            
        rstore = self.getRecordStore()
        # Store the full text in the record
        while not finished:
            try:
                data = urllib2.urlopen(record.link)
                record.full_text = articletxt.get_body_text(data.read())
                
                if not rstore.record_exists(record):
                    # Store the new record in the database.
                    rid = rstore.store(record)
            
                    # Generate a message for the annotation queue. 
                    msg = pq.Message()
                    msg.rid = rid 
                    outq.send(msg)
                    
                    added = True
                
                # Finished whether the record existed or not.
                finished = True
                    
            except ValueError, e:
                print "Error retrieving full text: ", e
                finished = True
            except HTTPError, e:
                print "HTTP Error:", e.code
                finished = True
            except URLError, e:
                print "URL Error:", e.reason
                finished = True
            except Exception, e:
                print "Could not find body text in ", record.link
                finished = True
            except httplib.IncompleteRead, e:
                attempts += 1
                print "Incomplete read...retrying (%s of 10 attempts)" % attempts
                if attempts == 10:
                    finished = True
        
        return added
    
    def execute(self, msg):
        print "Fetching from feed: %s" % (msg.url)
   
        feed_data = feedparser.parse(msg.url)
        channel, items = feed_data.feed, feed_data.entries
    
        outq = self.getOutputQueue()
        
        for item in items:
            record = db.Record()
            if item.has_key('title'):
                record.title = item['title']
            if item.has_key('updated_parsed'):
                record.pubDate = item['updated_parsed']
            if item.has_key('summary'):
                record.summary = ''.join(BeautifulSoup(item['summary']).findAll(text=True))
            if item.has_key('author'):
                record.author = item['author']
            if item.has_key('link'):
                record.link = item['link']
                
            rstore = self.getRecordStore()
            if not rstore.record_exists(record):
                # Store the new record in the database.
                rid = rstore.store(record)
            
                # Generate a message for the annotation queue. 
                msg = pq.Message()
                msg.rid = rid 
                outq.send(msg)
                    
    def runloop(self):
        in_queue = self.getInputQueue()
        in_queue.register_callback(self.execute)
        print "Launching reader with RSS plugin..."
        in_queue.start_waiting()
