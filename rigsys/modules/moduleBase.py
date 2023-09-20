"""Base class for all modules."""


class ModuleBase:
    """Base class for all modules."""

    def __init__(self) -> None:
        """Initialize the module."""
        self.buildOrder = 0
        self.dependencies = {}

    def run(self) -> None:
        """Run the module.

        Must be implemented by all modules.
        """
        pass
