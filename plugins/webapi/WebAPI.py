from poc.plugin import plugin
from poc.powerqueue import pq

import sys
import web
import socket
web.config.debug = True

urls = (
        '/api/v0/addtocorpus', 'AddToCorpus',
        '/api/v0/query', 'Query',
        )
# Set up the WSGI function.
# web.py 0.3+ way
app = web.application(urls, globals())
application = app.wsgifunc()
# web.py 0.2 way
#application = web.wsgifunc(web.webpyfunc(urls, globals()))

output_queue = pq.ProducerQueue("localhost", "preprocess.urlcrawl")

def queueUrl(url):
    message = pq.Message()
    message.url = url
    output_queue.send(message)

class AddToCorpus:
    def POST(self):
        i = web.input()
        url = i.url.strip()
        queueUrl(url)
        return "Adding %s to list to be fetched" % url

class Query:
    def GET(self):
        # Attempt to retrieve queried item from DB.
        
        # If item not in db:
        watcher_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        watcher_socket.connect(("127.0.0.1", 8128))
        watcher_socket.send("lawl\n")
        watcher_socket.shutdown(socket.SHUT_RDWR)
        watcher_socket.close()

        #    Register a postprocess id.
        #    Throw the URL in question into the crawl queue.
        #    Wait for the reply, or the maximum allowed latency.
        # Return reply.
        return "<html><head></head><body><h1>It works.</h1></body></html>"



class WebAPI(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(WebAPI, self).__init__()

    def init(self):
        #self.setRecordStoreHost('localhost')
        #self.setMatrixStoreHost('localhost')
        #self.setOutputQueueName('preprocess.crawl')
        pass

    def runloop(self):
        # Ridiculous hack to make self-hosted http server work
        sys.argv = ["launch.py", "8888"]
        # Run the WSGI server.
        # web.py 0.3+ way:
        app.run()
        # web.py 0.2 way:
        #web.run(urls, globals())

