import base64
import binascii
from Cryptodome.Hash import SHA256
from Cryptodome.PublicKey import RSA
from Cryptodome.Signature import PKCS1_v1_5


def verify(content, signature, public_key_):
    try:
        public_key = RSA.import_key(public_key_)
    except ValueError:
        return 0, "The format of public key is incorrect."
    verifier = PKCS1_v1_5.new(public_key)
    try:
        valid = verifier.verify(SHA256.new(content.encode("utf-8")), base64.b64decode(signature))
    except binascii.Error:
        return 0, "The padding of encoded signature is incorrect."
    return valid, str()


def generate(n=None):
    if n is None:
        n = 2048
    keypair = RSA.generate(n)
    private_key = keypair.export_key()
    public_key = keypair.public_key().export_key()
    return private_key, public_key


def sign(content, private_key_):
    try:
        private_key = RSA.import_key(private_key_)
    except ValueError:
        return str(), "The private key is invalid."
    signer = PKCS1_v1_5.new(private_key)
    try:
        signature = signer.sign(SHA256.new(content.encode("utf-8")))
    except TypeError:
        return str(), "The private key is invalid."
    signature = base64.encodebytes(signature).decode()
    return signature, str()


if __name__ == '__main__':
    # verify
    with open('tests/keypair.pub', 'r') as f:
        public_key_string = f.read()
    valid_, message = verify(
        content='cloudy-sfu',
        signature='yEUeH/O5jA2dTcxT1e/tNcDZ4q6Yyenit0qSO1OFetmBR9OHZG9REXwr0gfKIy3l/UR0yYVnvzqUnkwI1B6quL6QVLK4ImGdK'
                  '/bs3ArnAq/Oub/H2grxv0PGhp0uZ2jfP/JrrtAujlNOz4WJw5ZCMWEqT+a1Kc+Li/eIjUjBpAt37zI4xvgcqK+z3Ymk'
                  '/bL98eIyhyYLHzDp'
                  '/j19pxS4poBR2hln6wJZg75axxWdK8HVH1aA9AGQoM3YHoGMGbmgvBZrBf3qUwIgPdWpDD0SAkgnLeQCzO5NMpkLsHgcVGfOiZp'
                  'xcF2IjLXrIHrA3PDpnHHWUQ68mpFedtHvDguFcw==',
        public_key_=public_key_string
    )
    print(valid_, message)

    # sign
    with open('tests/keypair', 'r') as f:
        private_key_string = f.read()
    signature_, message = sign(
        content='cloudy-sfu',
        private_key_=private_key_string
    )
    print(signature_, message)
