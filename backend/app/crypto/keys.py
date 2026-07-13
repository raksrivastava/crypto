"""In-memory RSA keypair for the E2EE demo.

Generated once per process instead of embedding a static PEM literal in
source, so no key material ever lives in version control even as a mock.
"""
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.rsa import RSAPrivateKey


class RsaKeyPair:
    def __init__(self, key_size: int):
        self._private_key: RSAPrivateKey = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

    @property
    def private_key(self) -> RSAPrivateKey:
        return self._private_key

    @property
    def public_key_pem(self) -> str:
        pem = self._private_key.public_key().public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        return pem.decode("utf-8")


def load_key_pair(key_size: int) -> RsaKeyPair:
    return RsaKeyPair(key_size)
