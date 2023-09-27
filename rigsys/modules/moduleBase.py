"""Base class for all modules."""


class ModuleBase:
    """Base class for all modules."""

    def __init__(self) -> None:
        """Initialize the module."""
        self.name: str = ""
        self.buildOrder: int = 0
        self.dependencies: dict = {}
        self.ctrls: dict = {}
        self.isMuted: bool = False

    def run(self) -> None:
        """Run the module.

        Must be implemented by all modules.
        """
        pass
