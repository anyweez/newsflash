from poc.powerqueue import pq
from poc.plugin import plugin

def launch_similarity(plugin_name):

    user_plugin = plugin.load('similarity', plugin_name)
    user_plugin.init()
    
    in_queue = pq.ConsumerQueue('localhost', 'preprocess.similarity')
    in_queue.register_callback(user_plugin.execute)
    
    print "Launching annotator..."
    in_queue.start_waiting()

if __name__ == '__main__':
    launch_annotator()
