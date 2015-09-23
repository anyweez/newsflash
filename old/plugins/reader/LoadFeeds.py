from poc.plugin import plugin
from poc.powerqueue import pq

class LoadFeeds(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(LoadFeeds, self).__init__()

    def init(self):
        self.setOutputQueue('crawl')

    def runloop(self):
        queue = self.getOutputQueue()

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
