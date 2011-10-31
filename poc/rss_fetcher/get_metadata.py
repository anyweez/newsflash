import sys, hashlib, urllib2
import feedparser
from urllib2 import HTTPError, URLError

def feed_info(feed_url):
    feed_data = feedparser.parse(feed_url)
    channel, items = feed_data.feed, feed_data.entries
    
    info = []
    
    print 'Reading from %s (%s)' % (feed_url, channel['title'])
    for item in items:
        print item
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
        info.append(record)

        # If we've got a link to the article, pull that in and
        #   store it.  We need to figure out where to store this...
        if record.has_key('link'):
            filename = '../data/html/%s.html' % hashlib.md5(str(record)).hexdigest()
            # TODO: Can we make this asynchronous?
            try:
                data = urllib2.urlopen(record['link'])
            
                fp = open(filename, 'wb')
                fp.write(data.read())
                fp.close()
            except HTTPError, e:
                print "HTTP Error:",e.code , url
            except URLError, e:
                print "URL Error:",e.reason , url            
    return info

fp = open('rss.txt')
rss_urls = fp.readlines()
fp.close()


for url in rss_urls:
    data = feed_info(url)

sys.exit(0)

