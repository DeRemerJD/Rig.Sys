"""Proxy class for rigsys modules."""


class Proxy:
    """Proxy class for rigsys modules."""

    def __init__(self, position, rotation, side, label) -> None:
        """Initialize the proxy."""
        self.position = position
        self.rotation = rotation
        self.side = side
        self.label = label

    def build(self):
        """Build the proxy."""
        pass
