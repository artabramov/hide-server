"""Fernet helper for encrypt/decrypt values and files."""

from cryptography.fernet import Fernet
from app.config import get_cfg
from app.logger import get_log
from time import time

cfg = get_cfg()
log = get_log()
cipher_suite = Fernet(cfg.APP_FERNET_KEY)


class FernetMixin:
    """Fernet helper for encrypt/decrypt values and files."""

    @staticmethod
    def create_fernet_key() -> bytes:
        """Generate fernet key for config."""
        return Fernet.generate_key()
    
    def encrypt_value(self, value: str) -> str:
        """Encrypt string value."""
        encoded_text = cipher_suite.encrypt(str.encode(value))
        return encoded_text.decode()

    def decrypt_value(self, value: str) -> str:
        """Decrypt string value."""
        decoded_text = cipher_suite.decrypt(str.encode(value))
        return decoded_text.decode()

    async def encrypt_file(self, path: str):
        """Encrypt file."""
        with open(path, "rb") as fn:
            data = fn.read()
        encrypted_data = cipher_suite.encrypt(data)
        with open(path, "wb") as fn:
            fn.write(encrypted_data)

    async def decrypt_file(self, path: str) -> bytes:
        """Decrypt file to bytes object."""
        with open(path, "rb") as fn:
            encrypted_data = fn.read()
        return cipher_suite.decrypt(encrypted_data)
