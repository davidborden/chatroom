"""
Test file constructed from:

https://launchkey.com/docs/api/encryption
http://stackoverflow.com/questions/12524994/encrypt-decrypt-using-pycrypto-aes-256
http://eli.thegreenplace.net/2010/06/25/aes-encryption-of-files-in-python-with-pycrypto/
"""
import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto.Cipher import PKCS1_OAEP
from base64 import b64decode

def encrypt_RSA(public_key_loc, message):
  key = open(public_key_loc, "r").read()
  rsakey = RSA.importKey(key)
  rsakey = PKCS1_OAEP.new(rsakey)
  encrypted = rsakey.encrypt(message)
  return encrypted.encode('base64')

def decrypt_RSA(private_key_loc, package):
  key = open(private_key_loc, "r").read()
  rsakey = RSA.importKey(key)
  rsakey = PKCS1_OAEP.new(rsakey)
  decrypted = rsakey.decrypt(b64decode(package))
  return decrypted

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

if __name__ == "__main__":
  #Randomly generate a password of size 16 bytes that will be hashed into a 32 byte key.
  password = Random.new().read(AES.block_size)
  key = hashlib.sha256(password).digest()
  #Encrypt the  key using RSA (then simulate passing it over the network, as below)
  encrypted = encrypt_RSA('public_key.txt', key)
  #Receive the message and decrypt using RSA
  received_key = decrypt_RSA('private_key.txt', encrypted)

  #Now we know the symmetric AES key and can use it to encrypt a long message which will then be sent across the network
  c = AESCipher(received_key)
  p = c.encrypt("This is a secret message about watermelons! And unicorns. \nSo what if this message was really really big, like a paragraph or more. \nSo big that the text goes off the screen?")
  with open('test.txt', 'w') as file:
    file.write(p)
  with open('test.txt', 'r') as file:
    readFile = file.read()
  #Receive the message and decrypt
  print c.decrypt(readFile)
