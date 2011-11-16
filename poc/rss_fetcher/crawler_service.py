import hashlib, urllib2, sys
import feedparser

from poc.powerqueue import pq
from urllib2 import HTTPError, URLError

def get_meta(msg):
    print "Fetching from feed: %s" % (msg.url)
   
    feed_data = feedparser.parse(msg.url)
    channel, items = feed_data.feed, feed_data.entries
    
    #print 'Reading from %s (%s)' % (msg.url, channel['title'])
    for item in items:
        record = {}
        if item.has_key('title'):
            record['title'] = item['title']
        if item.has_key('link'):
            record['link'] = item['link']
        if item.has_key('updated_parsed'):
            record['pubDate'] = item['updated_parsed']
        if item.has_key('summary'):
            record['summary'] = item['summary']
        if item.has_key('author'):
            record['author'] = item['author']

        record_hash = hashlib.md5(str(record))

        # If we've got a link to the article, pull that in and
        #   store it.  We need to figure out where to store this...
        if record.has_key('link'):
            filename = 'poc/data/html/%s.html' % record_hash.hexdigest()
            # TODO: Can we make this asynchronous?
            try:
                data = urllib2.urlopen(record['link'])

                fp = open('%s' % filename, 'wb')
                fp.write(data.read())
                fp.close()
                
                record['full_html'] = filename
            except HTTPError, e:
                print "HTTP Error:", e.code , msg.url
            except URLError, e:
                print "URL Error:", e.reason , msg.url    
        
        write_record(record)
        # TODO: Send messages to preprocess.annotate.
        
def write_record(record):
    # Convert the record into a string.
    s = ' | '.join(['%s:%s' % (key, record[key]) for key in record.keys()])

    print s
    # Write the string to the end of the records file.
    fp = open('poc/data/records/rss.txt', 'a')
    fp.write('%s\n' % (s.encode('utf-8'),))
    fp.close()

def launch_crawler():
    in_queue = pq.ConsumerQueue('localhost', 'pending.crawl')
    in_queue.register_callback(get_meta)

    print "Launching metadata fetcher..."
    in_queue.start_waiting()

if __name__ == '__main__':
    launch_crawler()