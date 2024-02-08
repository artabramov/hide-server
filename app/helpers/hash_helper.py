"""Hash mixin."""

import hashlib
from app.config import get_cfg

cfg = get_cfg()


class HashHelper:
    """Hash mixin."""

    @staticmethod
    def get_hash(value: str) -> str:
        """Return hashed value."""
        encoded_value = (value + cfg.APP_HASH_SALT).encode()
        hash = hashlib.sha512(encoded_value)
        return hash.hexdigest()
