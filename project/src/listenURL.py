""" 
    PyQvod_v0.5: a python wrapper for Qvod downloader + wine 
    Author: yu239
    Date: 06/06/2012

    listenURL.py
    A simple server socket class that receives URL from javascript inside user browser
"""

import SocketServer
import Queue
from downloader import valid_url, download

_URL_QUEUE_ = None

class MyTCPHandler(SocketServer.BaseRequestHandler):

    def handle(self):
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        self.url = [l for l in self.data.split('\n') if l.startswith('qvod:')][0]
        self.status = 'invalid'
        print self.url
        if valid_url(self.url):
            self.status = 'ok'
        else:
            return
        
        # send back a HTTP header to tell the javascript the status
        self.response = 'HTTP/1.0 200 OK\r\n' + \
                        'Server: OneFile 1.0\r\n' + \
                        'Content-length: ' + str(len(self.status)) + '\r\n' + \
                        'Content-type: text/plain\r\n\r\n' + \
                        self.status
        self.request.sendall(self.response)
        # Put the received URL into queue
        if self.status == 'ok':
            if _URL_QUEUE_:
                _URL_QUEUE_.put(self.url)
            else:
                print self.url

def listenURL():
    HOST, PORT = "localhost", 62351
    
    # Create the server, binding to localhost on port 62351
    server = SocketServer.TCPServer((HOST, PORT), MyTCPHandler)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()


    
