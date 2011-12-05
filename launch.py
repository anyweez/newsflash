import sys
# Import the crawler service
from poc.rss_fetcher.crawler_service import launch_crawler
from poc.rss_fetcher.load_queue import load_feeds
from poc.annotator.annotator_service import launch_annotator
from poc.similarity.similarity_service import launch_similarity
    
services = {
    'crawler' : launch_crawler,
    'load_feeds' : load_feeds,
    'annotate' : launch_annotator,
    'similarity': launch_similarity,
}

if len(sys.argv) is not 3:
    print 'Please provide the name of the service to launch and an appropriate plugin.'
    print 'Known services:', ", ".join(services.keys())
    sys.exit(1)
    
service = sys.argv[1]
plugin_name = sys.argv[2]

if services.has_key(service):
    services[service](plugin_name)
else:
    print 'Unknown service requested: %s' % (service,)
    print 'The following services are available: %s' % (', '.join(services.keys()))
