"""
Version 1.0.0 (3/2/2014)
    -Initial release

    -Must now be run with the pycrypto library
    -Client must send an RSA encrypted AES key to the server upon initial connection
    -User data and conversation history is now stored as encrypted data with the server AES key hardcoded
    
    Generate the below with the generateRSA file in the repo
    -Server requires private_key.txt to run
    -Client requires public_key.txt to run

    TODO:
        -polish exception handling and broadcasted message formatting

Version 0.0.3 (3/1/2014)
    -Users must now login using a username/password combination
    -Users who aren't in the database must register before they're granted access to the chatroom
    -Users who claim to be in the database but aren't (and fail login) are disconnected after 3 attempts
    -Server now saves username/password information upon registration
    -Server now saves conversation log and displays it to the user upon login.

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
        -Server crashes in some odd instances (source of crash unknown due to rarity)
        -text formatting issues on client side
	-Does not notify other users when a user disconnects(only shown server side)
        -Does not notify other users when a user connects(only shown server side)

Encrypt/decrypt functions borrowed from:
    https://launchkey.com/docs/api/encryption
    http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
    http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
"""
import sys
import traceback
import time
from socket import *
from select import *
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64decode

class AESCipher:
    def __init__(self, key):
        self.bs = 32
        if len(key) >= 32:
            self.key = key[:32]
        else:
            self.key = self._pad(key)

    def encrypt(self, raw):
        raw = self._pad(raw)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw))

    def decrypt(self, enc):
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:]))

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    def _unpad(self, s):
        return s[:-ord(s[len(s)-1:])]

#map user to an ip and set a state for login
class User():
    def __init__(self, socket):
        self.userSocket = socket;
        self.userNAme = ''
	self.state = 'authenticate'
	#AESKey may need to be set to the empty string ""
	self.AESKey = None
	self.clientCipher = None
	#Each user gets an individual amount of attempts to login successfully
	self.currentUserAttempts = 0
	self.currentPasswordAttempts = 0
#enduserclass
def decrypt_RSA(private_key_loc, package):
  key = open(private_key_loc, "r").read()
  rsakey = RSA.importKey(key)
  rsakey = PKCS1_OAEP.new(rsakey)
  decrypted = rsakey.decrypt(b64decode(package))
  return decrypted

def AESEncrypt(userCipher, msg):
    return userCipher.encrypt(msg)
def AESDecrypt(userCipher, msg):
    return userCipher.decrypt(msg)
#endaesencrypt

class ChatRoom():
    def __init__(self, portnum):
        self.active = 1
        #Server AES initialization for writing/reading from encrypted files using
        #a constant password
        self.serverPassword = "I;l1k3!W4termLoN5_"
        self.key = hashlib.sha256(self.serverPassword).digest()
        self.serverCipher = AESCipher(self.key)
        self.unencryptedAccounts = ""
        try:
            self.users = {}
            with open('user_pass.txt', 'r') as file:
                #Decrypts the AES user/pass file
                self.unencryptedAccounts = self.serverCipher.decrypt(file.read())
                #Separates the unencrypted data into a list of user/passwords
                accountList = self.unencryptedAccounts.rstrip().split('\n')
                #Goes through the list and sorts the entries into the dictionary
                i = 0
                while i in range(len(accountList)-1):
                    self.users[accountList[i]] = accountList[i+1]
                    i += 2
                print self.users
        except:
            print "Problem loading user/password data."
            #traceback.print_exc()
        try:
            #Decrypts the AES conversation log
            with open('conversationLog.txt', 'r') as file:
                self.conversationLog = self.serverCipher.decrypt(file.read())
                print self.conversationLog
        except:
            print "Problem loading conversation file."
            self.conversationLog = ""
	self.port = int(portnum)
	#Max attempts for a user to login successfully using their user/pass combo
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
                    clientSocket, address = self.serverSocket.accept()
                    self.CONNECTED_SOCKETS.append(clientSocket)
                    print "Accepted new connection from", address
	    
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
                            #At the start of each if/else block decrypt the received MSG using AESDecrypt
                            for i in range(len(self.USER_LIST)):
                                #Accept the clients public key encryption
                                #If the client attempts to send anything other than a pubk enc then disconnect them
                                if self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'authenticate':
                                    #RSA Decrypt and receive the AES key here
                                    try:
                                        #Don't need to AESDecrypt this because it is RSA encrypted and we set the AES cipher afterwards
                                        self.USER_LIST[i].AESKey = decrypt_RSA('private_key.txt', msg)
                                        self.USER_LIST[i].clientCipher = AESCipher(self.USER_LIST[i].AESKey)
                                        print "Received and decrypted RSA/AES key"
                                    except:
                                        #Disconnect from user without message(temp fix for error raised on .send in this except
                                        #socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Failed key exchange. Disconnecting."))
                                        socket.close()
                                        self.CONNECTED_SOCKETS.remove(socket)
                                        print "Disconnected user for failing to exchange AES key"                                    
                                    #Notifies the user that the key has been accepted
                                    socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Connection accepted. Welcome to the chatroom!\n"))
                                    self.USER_LIST[i].state = 'signin'
                                
                                #Lets the user choose to make a new username or use an existing name
                                if self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'signin':
                                    msg = AESDecrypt(self.USER_LIST[i].clientCipher, msg).rstrip('\n')
                                    
                                    if msg == 'no':
                                        socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Enter username: "))
                                        self.USER_LIST[i].state = 'username'
                                    elif msg == 'yes':
                                        socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"New username: "))
                                        self.USER_LIST[i].state = 'create_user'
                                    else:
                                        socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"New user?(yes/no):"))
                                #If the user does not exist in the dictionary
                                elif self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'create_user':
                                    msg = AESDecrypt(self.USER_LIST[i].clientCipher, msg).rstrip('\n')
                                    if msg not in self.users:
                                        self.users[msg] = 'temp'                
                                        self.USER_LIST[i].userName = msg
                                        self.CONNECTED_USERS[socket] = msg
                                        socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Enter password: "))
                                        self.USER_LIST[i].state = 'create_password'
                                        #Using AES so write after password has been created
                                        self.unencryptedAccounts += msg + '\n' 
                                    else:
                                        socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"User already exists. Choose another username: "))
                                        
                                elif self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'create_password':
                                    msg = AESDecrypt(self.USER_LIST[i].clientCipher, msg).rstrip('\n')
                                    self.users[self.USER_LIST[i].userName] = msg
                                    if not self.conversationLog:
                                        socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Logged in. No conversation history to display."))
                                    else:
                                        socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Logged in.\n" + self.conversationLog))
                                    self.USER_LIST[i].state = 'logged_in'
                                    #Using AES so need to write to user/pass file all at once
                                    self.unencryptedAccounts += msg + '\n'
                                    with open('user_pass.txt', 'w') as file:
                                        file.write(self.serverCipher.encrypt(self.unencryptedAccounts))
                                #If the user already exists in the dictionary
                                elif self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'username':
                                    msg = AESDecrypt(self.USER_LIST[i].clientCipher, msg).rstrip('\n')
                                    if msg in self.users:
                                        socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Enter password: "))
                                        self.USER_LIST[i].state = 'password'
                                        self.USER_LIST[i].userName = msg
                                        self.CONNECTED_USERS[socket] = msg
                                    else:
                                        if self.USER_LIST[i].currentUserAttempts < self.maxAttempts:
                                            socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Enter username: "))
                                        else:
                                            socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Failed login. Disconnecting."))
                                            socket.close()
                                            self.CONNECTED_SOCKETS.remove(socket)
                                            print "Disconnected user attempting to connect with invalid credentials."
                                        self.USER_LIST[i].currentUserAttempts = self.USER_LIST[i].currentUserAttempts + 1
                                        
                                elif self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'password':
                                    msg = AESDecrypt(self.USER_LIST[i].clientCipher, msg).rstrip('\n')
                                    if msg == self.users[self.USER_LIST[i].userName]:
                                        self.USER_LIST[i].state = 'logged_in'
                                        if not self.conversationLog:
                                            socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Logged in. No conversation history to display."))
                                        else:
                                            socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Logged in.\n" + self.conversationLog))
                                    else:
                                        if self.USER_LIST[i].currentPasswordAttempts < self.maxAttempts:
                                            socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Enter password: "))
                                        else:
                                            socket.send(AESEncrypt(self.USER_LIST[i].clientCipher,"Failed login. Disconnecting."))
                                            socket.close()
                                            self.CONNECTED_SOCKETS.remove(socket)
                                            print "Disconnected user attempting to connect with invalid credentials."
                                        self.USER_LIST[i].currentPasswordAttempts = self.USER_LIST[i].currentPasswordAttempts + 1
                                        
                                elif self.USER_LIST[i].userSocket == socket and self.USER_LIST[i].state == 'logged_in':
                                    msg = AESDecrypt(self.USER_LIST[i].clientCipher, msg).rstrip('\n')
                                    #Only broadcast messages if the user is signed in
                                    bmsg = self.CONNECTED_USERS[socket] + ": " + msg
                                    print bmsg
                                    #Record conversation
                                    #Using AES need to write conversationLog all at once
                                    try:
                                        self.conversationLog += bmsg + '\n'
                                    except:
                                        traceback.print_exc()
                                    with open('conversationLog.txt', 'w') as file:
                                        file.write(self.serverCipher.encrypt(self.conversationLog))
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
            for i in range(len(self.USER_LIST)):
		if socket != self.serverSocket and socket != sendingSocket and socket == self.USER_LIST[i].userSocket:
			try:
				socket.send(AESEncrypt(self.USER_LIST[i].clientCipher, '\n' + bmsg))
			except:
				print "Could not send broadcast."
#endclass
#####
#Main
#####
if __name__ == "__main__":
    port = sys.argv[1]
    serverApp = ChatRoom(port)

