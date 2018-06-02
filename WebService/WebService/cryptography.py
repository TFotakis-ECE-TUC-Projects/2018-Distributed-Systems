import hashlib
import hmac
import json
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64decode, b64encode


class Cryptography:
	BS = AES.block_size
	# 32 byte key encoded as base64 string
	sharedKeyBase64 = 'UziKLGN2cWPns4SzwkPEeGxH/SQS5oOYqIrF2h7WbGs='
	sharedKey = b64decode(sharedKeyBase64)
	cipher = AES.MODE_CBC

	def pad(self, s):
		return s + (self.BS - len(s) % self.BS) * self.str_to_bytes(chr(self.BS - len(s) % self.BS))

	def unpad(self, s):
		return s[:-ord(s[len(s) - 1:])]

	def str_to_bytes(self, data):
		u_type = type(b''.decode('utf8'))
		if isinstance(data, u_type):
			return data.encode('utf8')
		return data

	def encrypt(self, plaintext, sharedKey, cipher):
		iv = Random.new().read(self.BS)
		encryption_suite = AES.new(sharedKey, cipher, iv)
		ciphertext_raw = encryption_suite.encrypt(self.pad(self.str_to_bytes(plaintext)))
		hmacHash = hmac.new(sharedKey, ciphertext_raw, hashlib.sha256).digest()
		ciphertext = b64encode(iv).decode("ascii") + ':' + b64encode(hmacHash).decode("ascii") + ':' + b64encode(ciphertext_raw).decode("ascii")
		return ciphertext

	def decrypt(self, ciphertext, sharedKey, cipher):
		parts = ciphertext.split(':')
		iv = b64decode(parts[0])
		hmacHash = b64decode(parts[1])
		ciphertext_raw = b64decode(parts[2])

		decryption_suite = AES.new(sharedKey, cipher, iv)
		plain_text = self.unpad(decryption_suite.decrypt(ciphertext_raw)).decode('utf-8')
		calcmac = hmac.new(sharedKey, ciphertext_raw, hashlib.sha256).digest()
		if hmacHash == calcmac:
			return plain_text
		else:
			return False

	def defaultEncrypt(self, inputData='', sharedKeyBase64=''):
		if sharedKeyBase64 != '':
			sharedKey = b64decode(sharedKeyBase64)
			data = self.encrypt(inputData, sharedKey, self.cipher)
		else:
			data = self.encrypt(inputData, self.sharedKey, self.cipher)
		result = {'error': '', 'data': data}
		print(json.JSONEncoder().encode(result))
		return result

	def defaultDecrypt(self, inputData='', sharedKeyBase64=''):
		if sharedKeyBase64 != '':
			sharedKey = b64decode(sharedKeyBase64)
			data = self.decrypt(inputData, sharedKey, self.cipher)
		else:
			data = self.decrypt(inputData, self.sharedKey, self.cipher)
		if not data:
			result = {'error': 'python decrypt failed', 'data': ''}
		else:
			result = {'error': '', 'data': data}
		print(json.JSONEncoder().encode(result))
		return result


cr = Cryptography()
