import sys
# Import the crawler service
from poc.rss_fetcher.crawler_service import launch_crawler
from poc.rss_fetcher.load_queue import load_feeds

if len(sys.argv) is not 2:
    print 'Please provide the name of the service to launch.'
    sys.exit(1)
    
service = sys.argv[1]

services = {
    'crawler' : launch_crawler,
    'load_feeds' : load_feeds
}

if services.has_key(service):
    services[service]()
else:
    print 'Unknown service requested: %s' % (service,)
    print 'The following services are available: %s' % (', '.join(services.keys()))