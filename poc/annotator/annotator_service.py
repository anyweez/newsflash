from poc.powerqueue import pq
from poc.plugin import plugin

def launch_annotator(plugin_name):

    user_plugin = plugin.load('annotator', plugin_name)
    user_plugin.init()
    
    in_queue = pq.ConsumerQueue('localhost', 'preprocess.annotate')
    in_queue.register_callback(user_plugin.execute)
    
    print "Launching annotator..."
    in_queue.start_waiting()

if __name__ == '__main__':
    launch_annotator()