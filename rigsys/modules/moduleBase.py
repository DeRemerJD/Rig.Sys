"""Base class for all modules."""


class ModuleBase:
    """Base class for all modules."""

    def __init__(self, rig, name: str = "", buildOrder: int = 0, isMuted: bool = False) -> None:
        """Initialize the module."""
        self.name: str = name
        if self.name == "":
            self.name = type(self).__name__

        self.buildOrder: int = buildOrder
        self.dependencies: dict = {}
        self.ctrls: dict = {}
        self.isMuted: bool = isMuted
        self.isRun: bool = False

        self._rig = rig

    def run(self) -> None:
        """Run the module.

        Must be implemented by all modules.
        """
        pass
