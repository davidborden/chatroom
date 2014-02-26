"""
Code constructed from two different sources:
	PyCrypto API Docs
			https://www.dlitz.net/software/pycrypto/api/current/
and
	Stackoverflow
			http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256


Use:
	Needs PyCrypto to run, install by typing:

		sudo easy_install pycrypto
 
	into the command line of your terminal(will probably prompt you for your password).
	If an error such as 'ImportError no module named pkg_resources' comes up during runtime then try the following:

		sudo easy_install setuptools -upgrade

	since pkg_resources depends on setuptools.
"""

from Crypto.Cipher import AES
from Crypto import Random
import base64

#Encryption start
key = b'Sixteen byte key'
#AES.block_size = 16
iv = Random.new().read(AES.block_size)
cipher = AES.new(key, AES.MODE_CFB, iv)
msg = iv + cipher.encrypt(b'Attack at dawn!')

#A decode error is output if base64 isn't used.
msg = base64.b64encode(msg)
print "Finished, here's the encrypted message:", msg

#Now decrypt
msg = base64.b64decode(msg)
iv = msg[:16]
decryptCipher = AES.new(key, AES.MODE_CFB, iv)
plaintxt = decryptCipher.decrypt(msg[16:])
print "Finished, here's the decrypted message:", plaintxt
