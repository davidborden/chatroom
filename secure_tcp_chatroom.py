"""
Version 0.0.1 (2/16/2014)
	-USAGE: run this program using the shell script "sh newServer_tcp.sh [PORT_NUMBER]"
		(i) Don't forget to save the PID from the shell script to terminate the program!
			-Ex: kill -15 PID
Known Issues:
	-if this program is not terminated first then the server goes into an infinite loop
	-does not broadcast received messages to all connected sockets(should be easy fix ->line 50)
"""
import sys
from socket import *
from select import *

class ChatRoom():
    def __init__(self, portnum):
        self.active = 1
	self.port = int(portnum)
        self.CONNECTED_SOCKETS = []
        self.serverSocket = socket(AF_INET, SOCK_STREAM)
        try:
	    print self.port
            self.serverSocket.bind(('', self.port))
        except:
            print "Could not bind port. Terminating."
            sys.exit()
        self.maxActiveConnections = 2
        self.MAX_RECV = 2048
        self.serverSocket.listen(self.maxActiveConnections)
	self.CONNECTED_SOCKETS.append(self.serverSocket)
        self.run()
    #endinit
        
    def run(self):
        while self.active:
            try:
                acceptedSockets, waitList, exceptList = select(self.CONNECTED_SOCKETS, [], [])
            except:
                print "Couldn't select(sockets)"

            for socket in acceptedSockets:
                if socket == self.serverSocket:
                    #accept username/password here, maybe 2 dictionaries
                    #1 for ip/username and another for username/pw?
                    clientSocket, address = self.serverSocket.accept()
                    self.CONNECTED_SOCKETS.append(clientSocket)
                    print "Accepted new connection from", address
                else:
                    try:
                        self.message = socket.recv(self.MAX_RECV)
                        print self.message
                    except:
                        print "Client disconnected. Terminating connection to the client."
                        socket.close()
                        CONNECTED_SOCKETS.remove(socket)
                        continue
            #endfor
        #endwhile
        self.serverSocket.close()
    #endrun
#####
#Main
#####
if __name__ == "__main__":
    port = sys.argv[1]
    serverApp = ChatRoom(port)

