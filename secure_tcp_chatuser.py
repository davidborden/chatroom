"""
Version 0.0.1 (2/17/2014)
	-USAGE: python secure_tcp_chatuser.py [HOST_NAME] [PORT_NUMBER]
	-Example: python secure_tcp_chatuser.py megatron.cs.ucsb.edu 5000

Known Issues:
	-if the user program is terminated first then the server side goes into an infinite loop
	-no prompt for user input
"""

import sys
from socket import *
from select import *

class ChatUser():
    def __init__(self, hostname, portnum):
        self.MAX_RECV = 2048
        self.host = hostname
	self.port = int(portnum)
        self.clientSocket = socket(AF_INET, SOCK_STREAM)
        try:
            self.clientSocket.connect((host, self.port))
            self.READABLE_STREAMS = [sys.stdin, self.clientSocket]
            self.active = 1
            self.run()
        except:
            print "Could not connect to server. Terminating"
            sys.exit()

    #endinit
    def run(self):
        while self.active:
            readableSockets, waitList, exceptList = select(self.READABLE_STREAMS, [], [])

            for socket in readableSockets:
                #message received from server
                if socket == self.clientSocket:
                    message = socket.recv(MAX_RECV)
                    if not message:
                        print "Disconnected from server."
                        sys.exit()
                    else:
                        print message
                #user entered message
                else:
                    userMessage = sys.stdin.readline()
                    self.clientSocket.send(userMessage)
            
        #endwhile
    #endrun

#endchatuser

#####
#Main
#####
if __name__ == "__main__":
    host = sys.argv[1]
    port = sys.argv[2]
    clientApp = ChatUser(host, port)

