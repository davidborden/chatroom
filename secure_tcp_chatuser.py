"""
Version 0.0.4 (3/2/2014)
    -Must now be run with the pycrypto library installed
    -Client sends AES key to server upon startup and received an accepted message when successful
        TODO:
            -AES encrypt individual messages sent to server

Version 0.0.2 (2/25/2014)
        Added the following functionality:
                -type "disconnect()" (no qoutes) or send whitespace input to the server to close
                        the connection from the client side without a server side freakout

	Cosmetic changes:
                -added a server side welcome message sent to the client upon connection
                -added a client side text prompt
                -added a "Client X has disconnected" server side message upon disconnect

Version 0.0.1 (2/17/2014)
	-USAGE: python secure_tcp_chatuser.py [HOST_NAME] [PORT_NUMBER]
	-Example: python secure_tcp_chatuser.py megatron.cs.ucsb.edu 5000

Known Issues (3/2/2014):
	-no client side issues known

Some functions borrowed from:
    https://launchkey.com/docs/api/encryption
    http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
    http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
"""

import sys
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64decode
from socket import *
from select import *

def encrypt_RSA(public_key_loc, message):
    key = open(public_key_loc, "r").read()
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    encrypted = rsakey.encrypt(message)
    return encrypted.encode('base64')

class ChatUser():
    def __init__(self, hostname, portnum):
        self.MAX_RECV = 2048
        self.host = hostname
        self.port = int(portnum)

        #Generate the AES key to be passed to the server
        #Randomly generate a password of size 16 bytes that will be hashed into a 32 byte key.
        self.password = Random.new().read(AES.block_size)
        self.key = hashlib.sha256(self.password).digest()
        #Encrypt the  key using RSA (then simulate passing it over the network, as below)
        self.encryptedAES = encrypt_RSA('public_key.txt', self.key)
        #Create initial login state
        self.state = 'init'
        
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

        #Before any other messages are sent, send the AES key using RSA
        if self.state == 'init':
            self.clientSocket.send(self.encryptedAES)
            self.state = 'signin'
        
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

