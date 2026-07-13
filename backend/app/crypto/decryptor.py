"""Clean abstraction over the asymmetric decryption layer.

Routes never touch the `cryptography` library directly; they depend on
this interface, so the crypto backend could be swapped without touching
request handling.
"""
import base64
import binascii
import json

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding

from app.crypto.keys import RsaKeyPair
from app.exceptions import DecryptionError, MalformedPayloadError

_OAEP_PADDING = padding.OAEP(mgf=padding.MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None)


class PayloadDecryptor:
    def __init__(self, key_pair: RsaKeyPair):
        self._key_pair = key_pair

    def decrypt(self, encrypted_data_b64: str) -> dict:
        ciphertext = self._decode_base64(encrypted_data_b64)
        plaintext = self._decrypt_rsa(ciphertext)
        return self._parse_identity_json(plaintext)

    @staticmethod
    def _decode_base64(value: str) -> bytes:
        try:
            return base64.b64decode(value, validate=True)
        except (ValueError, binascii.Error) as exc:
            raise DecryptionError("encrypted_data is not valid base64") from exc

    def _decrypt_rsa(self, ciphertext: bytes) -> bytes:
        try:
            return self._key_pair.private_key.decrypt(ciphertext, _OAEP_PADDING)
        except ValueError as exc:
            raise DecryptionError("Unable to decrypt payload with the configured key") from exc

    @staticmethod
    def _parse_identity_json(plaintext: bytes) -> dict:
        try:
            data = json.loads(plaintext)
        except json.JSONDecodeError as exc:
            raise MalformedPayloadError("Decrypted payload is not valid JSON") from exc
        if not isinstance(data, dict):
            raise MalformedPayloadError("Decrypted payload must be a JSON object")
        return data
