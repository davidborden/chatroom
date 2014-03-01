"""
Version 0.0.2 (2/25/2014)
        Added the following functionality:
                -type "disconnect()" (no qoutes) or send whitespace input to the server to close
                        the connection from the client side without a server side freakout

	Cosmetic changes:
                -added a server side welcome message sent to the client upon connection
                -added a client side text prompt
                -added a "Client X has disconnected" server side message upon disconnect
        TODO:
                -add broadcast feature
                -save log of chat conversations to file
                -add pycrypto RSA/AES

Version 0.0.1 (2/17/2014)
	-USAGE: python secure_tcp_chatuser.py [HOST_NAME] [PORT_NUMBER]
	-Example: python secure_tcp_chatuser.py megatron.cs.ucsb.edu 5000

Known Issues:
	-no client side issues known

#test change
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
		    try:
	            	message = socket.recv(self.MAX_RECV)
		    except:
		    	print "Could not receive message from server"
                    if not message:
			print message
                        print "Disconnected from server."
                        sys.exit()
                    else:
                        print message + '\n>',
                #user entered message
                else:
  		    print "\r>",
                    userMessage = sys.stdin.readline()
		    if userMessage.rstrip('\n') == "disconnect()":
		    	self.clientSocket.close()
			sys.exit()
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

