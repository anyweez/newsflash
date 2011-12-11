import ConfigParser
from poc.db import matrix
from poc.db import db
from poc.powerqueue import pq

def load(plugin_type, plugin_name):
    # Load the module from the plugins/ directory
    __import__( 'plugins.%s.%s' % (plugin_type, plugin_name) )
    mod = getattr(getattr(__import__('plugins'), plugin_type), plugin_name)
    
    # Return an instance of the particular object
    return getattr(mod, plugin_name)()


# Plugins should extend this base class and implement
#   the init() and execute() methods.
class BasePlugin(object):
    def __init__(self):
        config = ConfigParser.RawConfigParser()
        config.read('config.ini')
        self.params = {}
        self.params['similarity_batch_count'] = config.get('similarity', 'batch_count')
        self.params['crawl_host'] = config.get('queues', 'crawl_host')
        self.params['annotate_host'] = config.get('queues', 'annotate_host')
        self.params['similarity_host'] = config.get('queues', 'similarity_host')
        self.params['completed_host'] = config.get('queues', 'completed_host')
        self.params['object_host'] = config.get('storage', 'object_host')
        self.params['matrix_host'] = config.get('storage', 'matrix_host')
        
        self.record_store = None
        self.matrix_store = None

    # This should be overwritten by the plugin maker.  This will be
    #   called one time before the wave of execute()'s starts.
    def init(self):
        raise NotImplementedError
    
    # This should be overwritten by the plugin maker.  This will be
    #   called once per arriving event.
    def execute(self, msg):
        raise NotImplementedError
    
    def setInputQueue(self, name):
        qhost = self.getQueueHost(name)
        self.input_queue = pq.ConsumerQueue(qhost, name)
        
    def setOutputQueue(self, name):
        qhost = self.getQueueHost(name)
        self.output_queue = pq.ProducerQueue(qhost, name)

    def getInputQueue(self):
        return self.input_queue
    
    def getOutputQueue(self):
        return self.output_queue
    
    def getRecordStore(self):
        if self.record_store is None:
            host = self.getParam('object_host')
            self.record_store = db.RecordStore(host)
        return self.record_store
    
    def getMatrixStore(self):
        if self.matrix_store is None:
            host = self.getParam('matrix_host')
            self.matrix_store = matrix.CassandraMatrixStore(host)
        return self.matrix_store
    
    def getParam(self, param_name):
        return self.params[param_name]

    def getQueueHost(self, queue_name):
        return self.params[queue_name + '_host']
