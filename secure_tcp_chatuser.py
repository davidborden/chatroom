"""
Version 1.0.0 (3/2/2014)
    -Initial release

    -Must now be run with the pycrypto library installed
    -Client sends AES key to server upon startup and received an accepted message when successful

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
	-client side text formatting issues

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
from Crypto.Hash import HMAC
import traceback

def encrypt_RSA(public_key_loc, message):
    key = open(public_key_loc, "r").read()
    rsakey = RSA.importKey(key)
    rsakey = PKCS1_OAEP.new(rsakey)
    encrypted = rsakey.encrypt(message)
    return encrypted.encode('base64')
#enddef

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
#endaescipher

class HMACHash():
    def __init__(self,user_message):
        self.shared_salt = b'bAvId'
        print 'shared secret is: ', self.shared_salt
        self.hmacHasher = HMAC.new(self.shared_salt)
        self.mmesage = self.get_hmac_hash_and_message(user_message)
        #print 'in init: ', self.hmac_hash_and_message
        #return self.hmac_hash_and_message

    def get_hmac_hash_and_message(self,message):
        #self.salt_and_message = message + self.shared_salt
        printable_digest =  self.hmacHasher.hexdigest()
        print 'printable digest is: ', printable_digest
        mac_and_message = message + printable_digest
        print 'hex digest and message is: ', mac_and_message
        return mac_and_message
#endhmac

class ChatUser():
    def __init__(self, hostname, portnum):
        self.MAX_RECV = 2048
        self.host = hostname
        self.port = int(portnum)

        #Generate the AES key to be passed to the server
        #Randomly generate a password of size 16 bytes that will be hashed into a 32 byte key.
        self.password = Random.new().read(AES.block_size)
        self.key = hashlib.sha256(self.password).digest()
        #Generate the cipher using the hashed key
        self.clientCipher = AESCipher(self.key)
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
                        #Unencrypt AES message and print it out
                        unencryptedServerMessage = self.clientCipher.decrypt(message)
                        print unencryptedServerMessage
                        print "Disconnected from server."
                        sys.exit()
                    else:
                        unencryptedServerMessage = self.clientCipher.decrypt(message)
                        print unencryptedServerMessage + '\n>',
                #user entered message
                else:
                   
                    print "\r>",
                    userMessage = sys.stdin.readline()
                    if userMessage.rstrip('\n') == "disconnect()":
                        self.clientSocket.close()
                        sys.exit()
                    #AES encrypt message before sending it
                    self.hasher =  HMACHash(userMessage.rstrip('\n'))
                    hmac_message = self.hasher.mmesage
                    #print 'hmac_message is: ', hmac_message #self.hasher.mmesage
                    encryptedUserMessage = self.clientCipher.encrypt(hmac_message)
                    #print 'encrypted message is: ', encryptedUserMessage
                    self.clientSocket.send(encryptedUserMessage)
        
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

