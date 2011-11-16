from poc.powerqueue import pq

def load_feeds():
    # Create a connection to the output queue.
    queue = pq.ProducerQueue('localhost', 'preprocess.crawl')

    # Read in all of the RSS feeds from rss.txt
    fp = open('rss.txt', 'r')
    feeds = fp.readlines()
    fp.close()

    # Create a new message for all RSS feeds.
    for feed in feeds:
        msg = pq.Message()
        msg.url = feed
    
        # Send the message
        queue.send(msg)