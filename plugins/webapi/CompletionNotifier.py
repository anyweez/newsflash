from poc.plugin import plugin
from poc.powerqueue import pq

import sys
import threading
import asyncore
import socket

#class http_request_handler(asynchat.async_chat):
#    def __init__(self, sock, addr, sessions, log):
#        asynchat.async_chat.__init__(self, sock=sock)
#        self.addr = addr
#        self.sessions = sessions
#        self.ibuffer = []
#        self.obuffer = ""
#        self.set_terminator("\r\n\r\n")
#        self.reading_headers = True
#        self.handling = False
#        self.cgi_data = None
#        self.log = log
#
#    def collect_incoming_data(self, data):
#        """Buffer the data"""
#        self.ibuffer.append(data)
#
#    def found_terminator(self):
#        if self.reading_headers:
#            self.reading_headers = False
#            self.parse_headers("".join(self.ibuffer))
#            self.ibuffer = []
#            if self.op.upper() == "POST":
#                clen = self.headers.getheader("content-length")
#                self.set_terminator(int(clen))
#            else:
#                self.handling = True
#                self.set_terminator(None)
#                self.handle_request()
#        elif not self.handling:
#            self.set_terminator(None) # browsers sometimes over-send
#            self.cgi_data = parse(self.headers, "".join(self.ibuffer))
#            self.handling = True
#            self.ibuffer = []
#            self.handle_request()
#



class FrontendHandler(asyncore.dispatcher_with_send):
    def handle_read(self):
        print "Got data from", self.addr
        data = self.recv(8192)
        if data:
            #print data
            rid = str(data.strip())
            self.rid = rid
            print "Will notify", self.addr, "about updates to", rid
            if rid not in self.parent.parent.rid_to_waiters:
                self.parent.parent.rid_to_waiters[rid] = []
            self.parent.parent.rid_to_waiters[rid].append(self)
            #self.send(data)
    def handle_close(self):
        print "socket closed for", self.addr
        if hasattr(self, "rid"):
            print "rid was", self.rid
            print "self.parent.parent.rid_to_waiters =", self.parent.parent.rid_to_waiters
            self.parent.parent.rid_to_waiters[self.rid].remove(self)
            if len(self.parent.parent.rid_to_waiters[self.rid]) == 0:
                self.parent.parent.rid_to_waiters.remove(self.rid)


class CompletionServer(asyncore.dispatcher):
    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket(socket.AF_INET, socket.SOCK_STREAM)
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5) # Max concurrent requests

    def handle_accept(self):
        pair = self.accept()
        if pair is None:
            pass
        else:
            sock, addr = pair
            print 'Incoming connection from %s' % repr(addr)
            handler = FrontendHandler(sock)
            handler.parent = self


class CompletionNotifier(plugin.BasePlugin):
    def __init__(self):
        # Call your own constructor
        super(CompletionNotifier, self).__init__()
        self.rid_to_waiters = { } # Keep a list of rids that we should actually note the completions of, and map that to the handles to the sockets we should notify upon completion.

    def init(self):
        self.setInputQueue('completed')
        #self.setRecordStoreHost('localhost')
        #self.setMatrixStoreHost('localhost')
        pass

    def amqp_completed_msg(self, msg):
        print "Got process completion for", msg.primary, "for range", msg.secondary_min, "-", msg.secondary_max
        if msg.primary in self.rid_to_waiters:
            to_notify = self.rid_to_waiters[msg.primary]
            print "Will notify the following clients:"
            for client in to_notify:
                print "\t", client.addr
                client.send("%s %s" % (msg.secondary_min, msg.secondary_max))

    def handle_amqp(self):
        print "Launching AMQP thread..."
        #in_queue = pq.ConsumerQueue(, 'completed')
        in_queue = self.getInputQueue()
        in_queue.register_callback(self.amqp_completed_msg)
        in_queue.start_waiting()

    def run_server(self):
        print "Launching asyncore loop"
        self.server = CompletionServer("localhost", 8128)
        self.server.parent = self
        asyncore.loop()

    def runloop(self):
        # Fork a thread to listen on a socket for incoming queries
        self.server_thread = threading.Thread(target = self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()
        # Main thread listens for AMQP messages.
        self.handle_amqp()
        # AMQP stuff is messed up if we put it in a thread with a different self
        #self.amqp_thread = threading.Thread(target=self.handle_amqp)
        #self.amqp_thread.start()

        pass

