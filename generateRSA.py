"""
Taken from https://launchkey.com/docs/api/encryption
"""

from Crypto.PublicKey import RSA
def generate_RSA(bits=2048):
  '''
  Generate an RSA keypair with an exponent of 65537 in PEM format
  param: bits The key length in bits
  Return private key and public key
  '''
  new_key = RSA.generate(bits, e=65537)
  public_key = new_key.publickey().exportKey("PEM")
  private_key = new_key.exportKey("PEM")
  return private_key, public_key

if __name__ == "__main__":

  private_key, public_key = generate_RSA()

  with open('private_key.txt', 'w') as file:
    file.write(private_key)
  with open('public_key.txt', 'w') as file:
    file.write(public_key)
