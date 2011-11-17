from poc.powerqueue import pq
from poc.plugin import plugin

def launch_crawler(plugin_name):
    # Load and initialize the plugin.
    user_plugin = plugin.load('reader', plugin_name)
    user_plugin.init()
    
    in_queue = pq.ConsumerQueue('localhost', 'preprocess.crawl')
    in_queue.register_callback(user_plugin.execute)

    print "Launching reader with plugin %s..." % plugin_name.upper()
    in_queue.start_waiting()

if __name__ == '__main__':
    launch_crawler()
