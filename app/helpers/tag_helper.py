"""Hash mixin."""

import re


class TagHelper:
    """Hash mixin."""

    @staticmethod
    def get_tags(value: str) -> list:
        """Extract tags from content."""
        tags = re.findall('#(\w+)', value) if value else []
        return list(set([tag.lower() for tag in tags]))
