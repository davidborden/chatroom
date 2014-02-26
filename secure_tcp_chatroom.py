"""
Version 0.0.2 (2/25/2014)
	-confirmed multiple users can connect and send messages
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
	
Version 0.0.1 (2/16/2014)
	-USAGE: run this program using the shell script "sh newServer_tcp.sh [PORT_NUMBER]"
		(i) Don't forget to save the PID from the shell script to terminate the program!
			-Ex: kill -15 PID
Known Issues(2/25/2014):
	-does not broadcast received messages to all connected sockets(should be easy fix ->~line 50)
	-basically the entirety of the Except around line 63 isn't being called correctly(hence the
		almost identical if statement code around line 57)
"""
import sys
import time
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
		    clientSocket.send("Connection accepted. Welcome to the chatroom!\nEnter a message:")
                else:
		    #Message from client
                    try:
			#This is where the infinite loop is happening on client disconnect. 
			#It thinks there's a message when there isn't and it outputs a bunch of <'s
                        self.message = socket.recv(self.MAX_RECV)
			#TEMP FIX: When no input is sent then disconnect the user(occurs after 
                        #disconnect() command is sent)
			if self.message.rstrip('\n') == "":
				print "User %s disconnected." % address[0]
				socket.close()
				self.CONNECTED_SOCKETS.remove(socket)
				continue
                        print "< " + self.message.rstrip('\n')
                    except:
                        print "User %s disconnected." % address[0]
                        socket.close()
			try:
	                        self.CONNECTED_SOCKETS.remove(socket)
				continue
			except:
				print "Socket already removed from CONNECTED_SOCKETS"
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

