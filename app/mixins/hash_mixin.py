"""Hash mixin."""

import hashlib


class HashMixin:
    """Hash mixin."""

    def get_hash(self, value: str, salt: str) -> str:
        """Return hashed value."""
        encoded_value = (value + salt).encode()
        hash = hashlib.sha512(encoded_value)
        return hash.hexdigest()