import cgi
import hashlib
import hmac
import json
from Crypto import Random
from Crypto.Cipher import AES
from base64 import b64decode, b64encode

BS = AES.block_size


def pad(s):
	return s + (BS - len(s) % BS) * str_to_bytes(chr(BS - len(s) % BS))


def unpad(s):
	return s[:-ord(s[len(s) - 1:])]


def str_to_bytes(data):
	u_type = type(b''.decode('utf8'))
	if isinstance(data, u_type):
		return data.encode('utf8')
	return data


def encrypt(plaintext, sharedKey, cipher):
	iv = Random.new().read(BS)
	encryption_suite = AES.new(sharedKey, cipher, iv)
	ciphertext_raw = encryption_suite.encrypt(pad(str_to_bytes(plaintext)))
	hmacHash = hmac.new(sharedKey, ciphertext_raw, hashlib.sha256).digest()
	ciphertext = b64encode(iv).decode("ascii") + ':' + b64encode(hmacHash).decode("ascii") + ':' + b64encode(ciphertext_raw).decode("ascii")
	return ciphertext


def decrypt(ciphertext, sharedKey, cipher):
	parts = ciphertext.split(':')
	iv = b64decode(parts[0])
	hmacHash = b64decode(parts[1])
	ciphertext_raw = b64decode(parts[2])

	decryption_suite = AES.new(sharedKey, cipher, iv)
	plain_text = unpad(decryption_suite.decrypt(ciphertext_raw)).decode('utf-8')
	calcmac = hmac.new(sharedKey, ciphertext_raw, hashlib.sha256).digest()
	if hmacHash == calcmac:
		return plain_text
	else:
		return False


def test():
	print("Content-Type: application/json; charset=utf-8")
	print()

	form = cgi.FieldStorage()
	if "input" not in form or "method" not in form or form.getvalue("input") is None or form.getvalue("method") is None or form.getvalue("input") == "" or form.getvalue("method") == "":
		result = {'error': 'input or method is missing', 'data': ''}
		print(json.JSONEncoder().encode(result).encode('ascii'))
	else:
		inputData = form.getvalue("input")
		method = form.getvalue("method")

		#	32 byte key encoded as base64 string
		sharedKeyBase64 = '7vjTsO0IhSZsNA6ze37Dk/xXw2nphFM9ZAMUkwXgaAA='
		sharedKey = b64decode(sharedKeyBase64)
		cipher = AES.MODE_CBC

		result = {'error': '', 'data': ''}

		if method == 'encrypt':
			data = encrypt(inputData, sharedKey, cipher)
			result = {'error': '', 'data': data}
		elif method == "decrypt":
			data = decrypt(inputData, sharedKey, cipher)
			if not data:
				result = {'error': 'python decrypt failed', 'data': ''}
			else:
				result = {'error': '', 'data': data}
		else:
			result = {'error': 'method missing', 'data': ''}

		print(json.JSONEncoder().encode(result))
