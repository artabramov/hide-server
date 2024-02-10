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
        start_time = time()
        encoded_text = cipher_suite.encrypt(str.encode(value))
        res = encoded_text.decode()

        log.debug("Encrypt value, log_tag=fernet, elapsed_time=%s, value=%s, res=%s." % (
            time() - start_time, value, res))
        return res

    def decrypt_value(self, value: str) -> str:
        """Decrypt string value."""
        start_time = time()
        decoded_text = cipher_suite.decrypt(str.encode(value))
        res = decoded_text.decode()

        log.debug("Decrypt value, log_tag=fernet, elapsed_time=%s, value=%s, res=%s." % (
            time() - start_time, value, res))
        return res

    # async def encrypt_file(self, path: str) -> None:
    #     """Encrypt file."""
    #     with open(path, 'rb') as file:
    #         data = file.read()
    #     encrypted_data = self.cipher_suite.encrypt(data)
    #     with open(path, 'wb') as file:
    #         file.write(encrypted_data)

    # async def decrypt_file(self, path: str) -> bytes:
    #     """Decrypt file to bytes object."""
    #     with open(path, 'rb') as file:
    #         encrypted_data = file.read()
    #     data = self.cipher_suite.decrypt(encrypted_data)
    #     return data
