import hashlib, urllib2, sys
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
            try:
                data = urllib2.urlopen(record.link)
                #Store the full text in the record
                try:
                    record.full_text = articletxt.get_body_text(data.read())
                except ValueError, e:
                    print "Error retrieving full text: ", e
            except HTTPError, e:
                print "HTTP Error:", e.code
            except URLError, e:
                print "URL Error:", e.reason    
        if item.has_key('updated_parsed'):
            record.pubDate = item['updated_parsed']
        if item.has_key('summary'):
            record.summary = item['summary']
        if item.has_key('author'):
            record.author = item['author']
        
        if rstore.record_exists(record) is False:
            # Store the new record in the database.
            rid = rstore.store(record)
            
            # Generate a message for the annotation queue. 
            msg = pq.Message()
            msg.rid = rid 
            pqueue.send(msg)
            
            # Increment a counter.
            added += 1
            
    print "%d new articles added." % added
        # TODO: Send messages to preprocess.annotate.
        
def launch_crawler():
    in_queue = pq.ConsumerQueue('localhost', 'preprocess.crawl')
    in_queue.register_callback(get_meta)

    print "Launching metadata fetcher..."
    in_queue.start_waiting()

if __name__ == '__main__':
    launch_crawler()