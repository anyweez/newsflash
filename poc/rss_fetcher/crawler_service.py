import urllib2, httplib
import feedparser

from poc.db import db
from poc.powerqueue import pq
from poc.fulltext_parser import articletxt
from urllib2 import HTTPError, URLError

rstore = db.RecordStore('localhost')
pqueue = pq.ProducerQueue('localhost', 'preprocess.annotate')

def get_meta(msg):
    global rstore, pqueue
    
    print "Fetching from feed: %s" % (msg.url)
   
    feed_data = feedparser.parse(msg.url)
    channel, items = feed_data.feed, feed_data.entries
    
    #print 'Reading from %s (%s)' % (msg.url, channel['title'])
    added = 0
    for item in items:
        record = db.Record()
        if item.has_key('title'):
            record.title = item['title']
        if item.has_key('link'):
            record.link = item['link']
            
            finished = False
            attempts = 0
            # Store the full text in the record
            while not finished:
                try:
                    data = urllib2.urlopen(record.link)
                    record.full_text = articletxt.get_body_text(data.read())
                    finished = True
                except ValueError, e:
                    print "Error retrieving full text: ", e
                    finished = True
                except httplib.IncompleteRead, e:
                    attempts += 1
                    if attempts == 10:
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
                        
        if item.has_key('updated_parsed'):
            record.pubDate = item['updated_parsed']
        if item.has_key('summary'):
            record.summary = item['summary']
        if item.has_key('author'):
            record.author = item['author']
        
        # Require that stored records a) aren't already stored and b) have full text.
        if rstore.record_exists(record) is False and hasattr(record, 'full_text'):
            # Store the new record in the database.
            rid = rstore.store(record)
            
            # Generate a message for the annotation queue. 
            msg = pq.Message()
            msg.rid = rid 
            pqueue.send(msg)
            
            # Increment a counter.
            added += 1
            
    print "%d new articles added." % added
        
def launch_crawler():
    in_queue = pq.ConsumerQueue('localhost', 'preprocess.crawl')
    in_queue.register_callback(get_meta)

    print "Launching metadata fetcher..."
    in_queue.start_waiting()

if __name__ == '__main__':
    launch_crawler()
