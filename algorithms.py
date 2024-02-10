import base64
import binascii
from Cryptodome.Cipher import AES, PKCS1_OAEP
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Random import get_random_bytes
from Cryptodome.Signature import PKCS1_v1_5


def verify(content, signature, public_key):
    try:
        public_key = RSA.import_key(public_key)
    except ValueError:
        return 
    verifier = PKCS1_v1_5.new(public_key)
    try:
        decoded_signature = base64.b64decode(signature)
    except binascii.Error:
        return 
    valid = verifier.verify(SHA256.new(content), decoded_signature)
    return valid


def generate(n=2048):
    keypair = RSA.generate(n)
    private_key = keypair.export_key()
    public_key = keypair.public_key().export_key()
    return private_key, public_key


def sign(content, private_key):
    try:
        private_key = RSA.import_key(private_key)
    except ValueError:
        return
    signer = PKCS1_v1_5.new(private_key)
    try:
        signature = signer.sign(SHA256.new(content))
    except TypeError:  # the key is valid, but is a public key
        return
    signature = base64.encodebytes(signature).decode()
    return signature


def encrypt(content, public_key):
    try:
        public_key = RSA.import_key(public_key)
    except ValueError:
        return
    session_key = get_random_bytes(32)
    # Encrypt a session key with the public RSA key
    cipher_rsa = PKCS1_OAEP.new(public_key)
    encrypted_session_key = cipher_rsa.encrypt(session_key)
    # Raise error if using private key to encrypt
    try:
        cipher_rsa.decrypt(encrypted_session_key)
        return
    except TypeError:
        pass
    # Encrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX)
    encrypted_message, tag = cipher_aes.encrypt_and_digest(content)
    return {
        'encrypted_session_key': base64.encodebytes(encrypted_session_key).decode(),
        'nonce': base64.encodebytes(cipher_aes.nonce).decode(),
        'tag': base64.encodebytes(tag).decode(),
        'encrypted_message': base64.encodebytes(encrypted_message).decode()
    }


def decrypt(content, private_key):
    try:
        private_key = RSA.import_key(private_key)
    except ValueError:
        return 
    # Decrypt the session key with the private RSA key
    cipher_rsa = PKCS1_OAEP.new(private_key)
    try:
        encrypted_session_key = base64.b64decode(content.get('encrypted_session_key'))
        nonce = base64.b64decode(content.get('nonce'))
        tag = base64.b64decode(content.get('tag'))
        encrypted_message = base64.b64decode(content.get('encrypted_message'))
    except (TypeError, binascii.Error):
        return 
    try:
        session_key = cipher_rsa.decrypt(encrypted_session_key)
    except (AttributeError, ValueError, TypeError):
        return 
    # Decrypt the data with the AES session key
    cipher_aes = AES.new(session_key, AES.MODE_EAX, nonce)
    try:
        message = cipher_aes.decrypt_and_verify(encrypted_message, tag)
        return message
    except ValueError:
        return 
