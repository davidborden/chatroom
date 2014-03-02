"""
Version 0.0.3 (3/1/2013)
    -Users must now login using a username/password combination
    -Users who aren't in the database must register before they're granted access to the chatroom
    -Users who claim to be in the database but aren't (and fail login) are disconnected after 3 attempts
    -Server now saves username/password information upon registration
    -Server now saves conversation log and displays it to the user upon login.

    TODO:
        -add pycrypto RSA/AES
        -polish exception handling and broadcasted message formatting

Version 0.0.2 (2/25/2014)
	-Confirmed multiple users can connect and send messages tracked on the server 
	Cosmetic changes:
		-added a server side welcome message sent to the client upon connection
		-added a client side text prompt
		-added a "Client X has disconnected" server side message upon disconnect
	
Version 0.0.1 (2/16/2014)
	-USAGE: run this program using the shell script "sh newServer_tcp.sh [PORT_NUMBER]"
		(i) Don't forget to save the PID from the shell script to terminate the program!
			-Ex: kill -15 PID
Known Issues(3/1/2014):
	-Does not notify other users when a user disconnects(only shown server side)
        -Does not notify other users when a user connects(only shown server side)
"""
import sys
import traceback
import time
from socket import *
from select import *

#map user to an ip and set a state for login
class User():
    def __init__(self, socket):
        self.userSocket = socket;
        self.userNAme = ''
	self.state = 'signin'
	#Each user gets an individual amount of attempts to login successfully
	self.currentUserAttempts = 0
	self.currentPasswordAttempts = 0
#enduserclass

class ChatRoom():
    def __init__(self, portnum):
        self.active = 1
        try:
            self.users = {}
            with open('user_pass.txt', 'r') as file:
                while True:
                    u = file.readline()
                    p = file.readline()
                    if not p:
                        break #EOF
                    self.users[u.rstrip('\n')] = p.rstrip('\n')
                    print self.users
        except:
            print "Problem loading user/password data."
            #traceback.print_exc()
        try:
            with open('conversationLog.txt', 'r') as file:
                self.conversationLog = file.read()
                print self.conversationLog
        except:
            print "Problem loading conversation file."
            self.conversationLog = None
	self.port = int(portnum)
	self.maxAttempts = 2
        self.CONNECTED_SOCKETS = []
        #The user_list is a list of User objects that is specifically for storing the login state of a connected user
	self.USER_LIST = []
	#The connected_users list allows the server to pair username with broadcast messages
	self.CONNECTED_USERS = {}
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
		    clientSocket.send("Connection accepted. Welcome to the chatroom!\nNew user?(yes/no):")
	    
                    self.USER_LIST.append(User(clientSocket))
                else:
		    #Message received from client
                    try:
			#This is where the infinite loop is happening on client disconnect. 
			#It thinks there's a message when there isn't and it outputs a bunch of <'s
                        self.message = socket.recv(self.MAX_RECV)
                        msg = self.message.rstrip('\n')
			#TEMP FIX FOR THE ABOVE: When no input is sent then disconnect the user(occurs after 
                        #disconnect() command is sent)
			if msg == "":
                            print "User %s disconnected." % self.CONNECTED_USERS[socket]
                            socket.close()
                            self.CONNECTED_SOCKETS.remove(socket)
                            continue
			else:
                            #Checks for login status
                            for i in range(len(self.USER_LIST)):
                                #Lets the user choose to make a new username or use an existing name
                                if self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'signin':
                                    if msg == 'no':
                                        socket.send("Enter username: ")
                                        self.USER_LIST[i].state = 'username'
                                    elif msg == 'yes':
                                        socket.send("New username: ")
                                        self.USER_LIST[i].state = 'create_user'
                                    else:
                                        socket.send("New user?(yes/no):")
                                #If the user does not exist in the dictionary
                                elif self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'create_user':
                                    if msg not in self.users:
                                        self.users[msg] = 'temp'                
                                        self.USER_LIST[i].userName = msg
                                        self.CONNECTED_USERS[socket] = msg
                                        socket.send("Enter password: ")
                                        self.USER_LIST[i].state = 'create_password'
                                        with open('user_pass.txt', 'a') as file:
                                            file.write(msg + '\n')
                                    else:
                                        socket.send("User already exists. Choose another username: ")
                                        
                                elif self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'create_password':
                                    self.users[self.USER_LIST[i].userName] = msg
                                    if not self.conversationLog:
                                        socket.send("Logged in. No conversation history to display.")
                                    else:
                                        socket.send("Logged in.\n" + self.conversationLog)
                                    self.USER_LIST[i].state = 'logged_in'
                                    with open('user_pass.txt', 'a') as file:
                                        file.write(msg + '\n')
                                #If the user already exists in the dictionary
                                elif self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'username':
                                    if msg in self.users:
                                        socket.send("Enter password: ")
                                        self.USER_LIST[i].state = 'password'
                                        self.USER_LIST[i].userName = msg
                                        self.CONNECTED_USERS[socket] = msg
                                    else:
                                        if self.USER_LIST[i].currentUserAttempts < self.maxAttempts:
                                            socket.send("Enter username: ")
                                        else:
                                            socket.send("Failed login. Disconnecting.")
                                            socket.close()
                                            self.CONNECTED_SOCKETS.remove(socket)
                                            print "Disconnected user attempting to connect with invalid credentials."
                                        self.USER_LIST[i].currentUserAttempts = self.USER_LIST[i].currentUserAttempts + 1
                                        
                                elif self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'password':
                                    if msg == self.users[self.USER_LIST[i].userName]:
                                        self.USER_LIST[i].state = 'logged_in'
                                        if not self.conversationLog:
                                            socket.send("Logged in. No conversation history to display.")
                                        else:
                                            socket.send("Logged in.\n" + self.conversationLog)
                                    else:
                                        if self.USER_LIST[i].currentPasswordAttempts < self.maxAttempts:
                                            socket.send("Enter password: ")
                                        else:
                                            socket.send("Failed login. Disconnecting.")
                                            socket.close()
                                            self.CONNECTED_SOCKETS.remove(socket)
                                            print "Disconnected user attempting to connect with invalid credentials."
                                        self.USER_LIST[i].currentPasswordAttempts = self.USER_LIST[i].currentPasswordAttempts + 1
                                        
                                elif self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'logged_in':
                                    #Only broadcast messages if the user is signed in
                                    bmsg = self.CONNECTED_USERS[socket] + ": " + msg
                                    print bmsg
                                    #Record conversation
                                    #self.conversationLog = conversationLog + bmsg
                                    with open('conversationLog.txt', 'a') as file:
                                        file.write(bmsg + '\n')
                                    try:
                                        self.broadcast(bmsg, socket)
                                    except:
                                        print "Problem broadcasting."

                    except:
                        print "User %s disconnected." % self.CONNECTED_USERS[socket]
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
    def broadcast(self, bmsg, sendingSocket):
	for socket in self.CONNECTED_SOCKETS:
		if socket != self.serverSocket and socket != sendingSocket:
			try:
				socket.send('\n' + bmsg)
			except:
				print "Could not send broadcast."
#endclass
#####
#Main
#####
if __name__ == "__main__":
    port = sys.argv[1]
    serverApp = ChatRoom(port)

