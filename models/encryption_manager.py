import os
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding

class EncryptionManager:
    
    _private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=1024
    )
    
    _public_key = _private_key.public_key()
    
    public_key_bytes = _public_key.public_bytes(
        encoding=serialization.Encoding.DER,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

    @staticmethod
    def generate_verify_token() -> bytes:
        return os.urandom(4)

    @staticmethod
    def decrypt_shared_secret(encrypted_secret: bytes) -> bytes:
        return EncryptionManager._private_key.decrypt(
            encrypted_secret,
            padding.PKCS1v15()
        )

    @staticmethod
    def decrypt_verify_token(encrypted_token: bytes) -> bytes:
        return EncryptionManager._private_key.decrypt(
            encrypted_token,
            padding.PKCS1v15()
        )