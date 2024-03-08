"""Pydantic primary schema."""

from pydantic import BaseModel


class PrimarySchema(BaseModel):
    """Pydantic primary schema."""

    @property
    def kwargs(self):
        """Get schema attributes."""
        return {key[0]: key[1] for key in self if key[1]}
