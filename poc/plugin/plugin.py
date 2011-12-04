from poc.db import db
from poc.db import matrix
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
        pass

    # This should be overwritten by the plugin maker.  This will be
    #   called one time before the wave of execute()'s starts.
    def init(self):
        raise NotImplementedError
    
    # This should be overwritten by the plugin maker.  This will be
    #   called once per arriving event.
    def execute(self, msg):
        raise NotImplementedError
    
    def setInputQueueName(self, host, name):
        self.input_queue = pq.ConsumerQueue(host, name)
        
    def setOutputQueueName(self, host, name):
        self.output_queue = pq.ProducerQueue(host, name)
        
    def setRecordStoreHost(self, host):
        self.record_store = db.RecordStore(host)

    def setMatrixStoreHost(self, host):
        self.matrix_store = matrix.MatrixStore(host)
        
    def getInputQueue(self):
        return self.input_queue
    
    def getOutputQueue(self):
        return self.output_queue
    
    def getRecordStore(self):
        return self.record_store
    
    def getMatrixStore(self):
        return self.matrix_store