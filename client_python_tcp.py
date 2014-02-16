"""Lines 1-15 taken from the textbook Computer Networking 6th edition
by Kurose and Ross, p. 190"""

import sys
import uuid
from socket import *
from struct import *


def readHeaderType(receivedStream):

        decodedHeaderType = unpack('!B', receivedStream[0])
        return decodedHeaderType

#should be entered if and only if a command with a message attached is sent to the client
def readHeaderMessageLength(socket, receivedStream):

        #Keeps reading in data until the entire header is received(either 5 or 37 bytes in length)
        while len(receivedStream) < 5:
                receivedStream = receivedStream + socket.recv(5-len(receivedStream))

        #Bytes 1-5 are always the message length(not including the UUID) if a header exists
        #and a message is attached(in other words, if this function was entered in the first place)
        decodedHeader = unpack('!I', receivedStream[1:5])
        return int(decodedHeader[0])

def readMessage(socket, receivedStream, messageLength, index):
        message = ""

        #Loads more bytes if the receivedStream doesn't initially have enough
        if len(receivedStream) < messageLength:
                receivedStream = receivedStream + socket.recv(8)
        while len(message) < messageLength:
                message = message + receivedStream[index]
                index = index + 1
                if len(message) < messageLength and index >= len(receivedStream):
                        receivedStream = receivedStream + socket.recv(messageLength - len(message))
        #End while
        return message

userID = ""
serverName = 'localhost'
#Sets the port based on argument in sys.argv[1]
serverPort = int(sys.argv[1])
if serverPort < 1024 or serverPort > 49151:
	print "Invalid port. Terminating."
	sys.exit()

clientSocket = socket(AF_INET, SOCK_STREAM)

#Initialization
try:
	clientSocket.connect((serverName, serverPort))
except:
	print "Could not connect to server. Terminating."
	sys.exit()

username = sys.argv[2]
"""
Format for the packing of the header
!BI signifies network/unsigned char/unsigned int for a total of 5 bytes
"""
headerType = pack('!B', 1)
headerLength = pack('!I', len(username))
packet = headerType + headerLength + username
clientSocket.send(packet)
#check to see if userID sent back, if not, throw error
try:
	receivedStream = clientSocket.recv(8)
	while len(receivedStream) < 1:
		receivedStream = receivedStream + clientSocket.recv(8)

	messageType = readHeaderType(receivedStream)
	if messageType[0] == 2:
		messageLength = readHeaderMessageLength(clientSocket, receivedStream)
		userID = readMessage(clientSocket, receivedStream, messageLength, 5)
	else:
		print "Invalid server initialization. Terminating."
except:
	print "Invalid server initialization. Terminating."
connected = True
#End of initialization -> welcome message should be in the stream, even if it's empty there should be 0x05 sent

def grabMessage(clientSocket):
	receivedStream = ""
	while len(receivedStream) < 1:
		receivedStream = receivedStream + clientSocket.recv(1-len(receivedStream))
	
	messageType = readHeaderType(receivedStream)
	messageLength = readHeaderMessageLength(clientSocket, receivedStream)
	receivedStream = ""
	message = readMessage(clientSocket, receivedStream, messageLength, 0)
	return message

print "Welcome message: %s" % grabMessage(clientSocket)

#Menu loop
while connected:

	

	command = raw_input("Enter a command: (send, print, or exit)\n")
	if command == "exit":
		headerType = pack('!B', 6)
		clientSocket.send(headerType)
		clientSocket.close()
		connected = False
	elif command == "print":
		headerType = pack('!B', 3)
		clientSocket.send(headerType)
		#receive some stuff
		print grabMessage(clientSocket)
	elif command == "send":
		message = raw_input("Enter your message:\n")
		headerType = pack('!B', 4)
		messageLength = 32 + len(message)
		headerLength = pack('!I', messageLength)
		packet = headerType + headerLength + userID + message
		clientSocket.send(packet)

	else:
		continue	
#End while	
