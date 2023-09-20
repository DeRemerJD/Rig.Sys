"""Rig API module."""


class Rig:
    """Rig class."""

    def __init__(self) -> None:
        """Initialize the rig."""
        self.motionModules = {}
        self.deformerModules = {}
        self.utilityModules = {}
        self.exportModules = {}
