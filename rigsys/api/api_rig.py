"""Rig API module."""


class Rig:
    """Rig class."""

    def __init__(self) -> None:
        """Initialize the rig."""
        self.motionModules = {}
        self.deformerModules = {}
        self.utilityModules = {}
        self.exportModules = {}

    def build(self, buildLevel: int = -1) -> bool:
        """Build the rig up to the specified level.

        Args:
            buildLevel (int, optional): The level to which the rig should be built. Defaults to -1, which means all
                modules will be built.

        Returns:
            bool: True if successful, False otherwise.
        """
        success = True

        # TODO: Implement. Figure out how to get the build order of the modules.
        # TODO: Logging

        return success
