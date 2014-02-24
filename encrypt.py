#Vars
n = 3727264081
e = 65537
d = 3349121513

#The length of this message has to be k-11 bytes long where k is
#the number of bytes needed to encode n
message = "hi"

#Converts the message to hex
enc = message.encode("hex")

#Converts the hex to an int
m = int(enc, 16)

#This is c = m^e mod n from the slides.
#Using pow(m,e,n) is a lot more efficient than using pow(m,e) % n
c = pow(m, e, n)
print "This is the encrypted message:"
print c

#Equivalent to m = c^d mod n from the slides.
t = pow(c,d, n)

#Change the int back to hex
t2 = hex(t)

#Strip off any '0x' prepended or 'L' (for Long) appended
t2 = t2[2:].rstrip("L")

#Convert back to string from hex
unencryptedMessage = t2.decode("hex")

#Output message
print "This is the unencrypted message:"
print unencryptedMessage


