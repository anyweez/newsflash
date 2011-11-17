from poc.db import db
from poc.powerqueue import pq

def load(plugin_type, plugin_name):
    # Load the module from the plugins/ directory
    __import__( 'plugins.%s.%s' % (plugin_type, plugin_name) )
    mod = getattr(getattr(__import__('plugins'), plugin_type), plugin_name)
    
    # Return an instance of the particular object
    return getattr(mod, plugin_name)()


# Plugins should extend this base class and implement
#   the execute() method.
class BasePlugin(object):
    def __init__(self):
        pass

    # This should be overwritten by the plugin maker.
    def init(self):
        raise NotImplementedError
    
    # This should be overwritten by the plugin maker.
    def execute(self, msg):
        raise NotImplementedError
    
    def setInputQueueName(self, host, name):
        self.input_queue = pq.ConsumerQueue(host, name)
        
    def setOutputQueueName(self, host, name):
        self.output_queue = pq.ProducerQueue(host, name)
        
    def setRecordStoreHost(self, host):
        self.record_store = db.RecordStore(host)

    # TODO: This doesn't work yet.
    def setMatrixStoreHost(self, host):
        self.matrix_store = None
        raise NotImplementedError
        
    def getInputQueue(self):
        return self.input_queue
    
    def getOutputQueue(self):
        return self.output_queue
    
    def getRecordStore(self):
        return self.record_store
    
    # TODO: This doesn't work yet.
    def getMatrixStore(self):
        raise NotImplementedError