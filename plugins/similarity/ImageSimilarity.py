import PIL.Image as Image
from poc.plugin import plugin
from poc.powerqueue import pq
import sys
import time

class ImageSimilarity(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(ImageSimilarity, self).__init__()

    def init(self):
        self.setOutputQueue('completed')
        self.setInputQueue('similarity')

    def execute(self, msg):
        secondary = int(msg.secondary_min)
        while secondary < (int(msg.secondary_max) + 1):
            print time.time(), "similarity %s and %s" % (msg.primary, secondary)
            rstore = self.getRecordStore()

            r1 = rstore.get(msg.primary)
            r2 = rstore.get(secondary)
            
            # Check to see if the histograms exist for r2.  They are guaranteed to exist
            #   for r1.  r1 and r2 are both guaranteed to exist in the database.
            if hasattr(r2, 'r_hist') and hasattr(r2, 'g_hist') and hasattr(r2, 'b_hist') :
                # Difference in individual histogram values seems
                #   to work pretty well.
                r_delt = sum([abs(a - b) for a, b in zip(r1.r_hist, r2.r_hist)])
                g_delt = sum([abs(a - b) for a, b in zip(r1.g_hist, r2.g_hist)])
                b_delt = sum([abs(a - b) for a, b in zip(r1.b_hist, r2.b_hist)])

                mstore = self.getMatrixStore()
                # In my tests it seems like 2 is the largest delta
                #   value that can be generated for a single channel.
                #   Since there are three channels, the max value is
                #   6.  Invert and normalize to fall between the range
                #   [0, 1] where higher = more similar.
                similarity = (6 - (r_delt + g_delt + b_delt)) / 6
                mstore.set_val(x=msg.primary, y=secondary, val=similarity)
        
                secondary += 1
            else:
                # Otherwise the data hasnt' been set yet and we should bail for now.
                self.defer(msg)
                return
        # Pass the same message that we received.
        outq = self.getOutputQueue()    
        outq.send(msg)
            

    def runloop(self):
        in_queue = self.getInputQueue()
        in_queue.register_callback(self.execute)
        print >> sys.stderr, "Launching similarity..."
        in_queue.start_waiting()
