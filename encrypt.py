#Vars
n = 3727264081
e = 65537
d = 3349121513

#The length of this message has to be k-11 bytes long where k is
#the number of bytes needed to encode n
message = "hi"

enc = message.encode("hex")
m = int(enc, 16)
c = pow(m, e, n)
print "This is the encrypted message:"
print c

t = pow(c,d, n)
t2 = hex(t)
print t2
t2 = t2[2:].rstrip("L")
print t2
unencryptedMessage = t2.decode("hex")
print "This is the unencrypted message:"
print unencryptedMessage


