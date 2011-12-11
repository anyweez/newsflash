from poc.plugin import plugin
from poc.powerqueue import pq

class OfflineDB(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(OfflineDB, self).__init__()
        
    def init(self):
        self.setOutputQueue('annotate')
    
    def execute(self, msg):
        pqueue = self.getOutputQueue()
        rs = self.getRecordStore() 
        msg = pq.Message()
        
        result = rs.execute("SELECT rid FROM records")
        for rid in [int(rid[0]) for rid in result]:
            msg.rid = rid
            pqueue.send(msg)
