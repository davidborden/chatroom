"""Lines x-x taken from the textbook Computer Networking 6th edition
by Kurose and Ross, p.193"""

import sys
import random
import uuid
import collections
from socket import *
from struct import *

boardMessages = ""
welcomeMessage = ""
currentUser = ""
previousCommand = ""
connected = False
dict = {}

def initializeConnection(socket, dict):
        receivedStream = socket.recv(8)
        while len(receivedStream) < 1:
                receivedStream = receivedStream + socket.recv(8)
        #this expects an initialization byte i.e. 0x01
        messageType = readHeaderType(receivedStream)
        if(messageType[0] == 1):
                messageLength = readHeaderMessageLength(socket, receivedStream)
                username = readMessage(socket, receivedStream, messageLength, 5)
                #Add the username to the dictionary after generating a UUID
                userID = uuid.uuid4().hex
                dict[userID] = username

                #Send the UUID generated back to the client
                headerType = pack('!B', 2)
                headerLength = pack('!I', len(userID))
                packet = headerType + headerLength + userID
                socket.send(packet)
        else:
                print "Invalid Initialization. Terminating"
                sys.exit()

        return dict


#while the connection is active
def readHeaderType(receivedStream):

        decodedHeaderType = unpack('!B', receivedStream[0])
        return decodedHeaderType

#should be entered if and only if a command with a message attached is sent to the server
def readHeaderMessageLength(socket, receivedStream):

        #Keeps reading in data until the entire header is received(either 5 or 37 bytes in length)
        while len(receivedStream) < 5:
                receivedStream = receivedStream + socket.recv(5-len(receivedStream))

        #Bytes 1-5 are always the message length(not including the UUID) if a header exists
        #and a message is attached(in other words, if this function was entered in the first place)
        decodedHeader = unpack('!I', receivedStream[1:5])
        return int(decodedHeader[0])

def readUUID(socket, receivedStream):
        UUID = ""
        i = 0
        if len(receivedStream) < 32:
                receivedStream = receivedStream + socket.recv(8)
        while len(UUID) < 32 and i < len(receivedStream):
                UUID = UUID + receivedStream[i]
                i = i + 1

                """
                If the entire UUID(which isn't packed, it's sent over as 32 byte hex)
                isn't received when the counter variable 'i' gets to the end of the receivedStream
                buffer, then load more of the socket stream into the receivedStream and read the rest
                of the UUID
                """
                if len(UUID) < 32 and i >= len(receivedStream):
                        receivedStream = receivedStream + socket.recv(32 - len(UUID))
        #End while
        return UUID


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


#Valid ports = 1,024 - 49151
serverPort = int(sys.argv[1])

if serverPort < 1024 or serverPort > 49151:
        print "Invalid port. Terminating."
        sys.exit()

serverSocket = socket(AF_INET, SOCK_STREAM)

try:
        serverSocket.bind(('pinky.cs.ucsb.edu', serverPort))
except:
        print "Could not bind port. Terminating."
        sys.exit()

#Listens with a max of 1 connection
serverSocket.listen(2)

#Needs to be removed eventually

#Reads the welcome.txt
for line in sys.stdin:
  welcomeMessage += line

while 1:
        #Initialization
        connectionSocket, addr = serverSocket.accept()
        dict = initializeConnection(connectionSocket, dict)

        #Send welcome message
        headerType = pack('!B', 5)
        headerLength = pack('!I', len(welcomeMessage))
        packet = headerType + headerLength + welcomeMessage
        connectionSocket.send(packet)
        connected = True
        #End initialization

        #receivedStream is reset to empty several times because that denotes that the data that was in that variable
        #temporarily has been read and is no longer needed
	
        while connected:
                receivedStream = ""
                while len(receivedStream) < 1:
                        receivedStream = receivedStream + connectionSocket.recv(1-len(receivedStream))

                messageType = readHeaderType(receivedStream)
                if messageType[0] == 3:
                        headerType = pack('!B', 5)
                        headerLength = pack('!I', len(boardMessages))
                        packet = headerType + headerLength + boardMessages
                        connectionSocket.send(packet)
                elif messageType[0] == 4:
                        messageLength = readHeaderMessageLength(connectionSocket, receivedStream)
                        receivedStream = ""
                        userID = readUUID(connectionSocket, receivedStream)
                        receivedStream = ""
                        message = readMessage(connectionSocket, receivedStream, messageLength-32, 0)

                        #Validate the message
                        try:
                                if dict[userID]:
                                        outputMessage = dict[userID] + ": " + message + "\n"
                                        boardMessages = boardMessages + outputMessage + "\n"
                        except:
                                #the userID doesn't exist in the dictionary
                                connectionSocket.close()
                                connected = False
                                break
                elif messageType[0] == 6:
                        connectionSocket.close()
                        connected = False
                        break
                else:
                        connectionSocket.close()
                        connected = False
                        break
        #End while
        print "Connection closed"

