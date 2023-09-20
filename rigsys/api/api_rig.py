"""Rig API module."""


BUILD_PROXIES = "build_proxies"
BUILD_MODULES = "build_modules"
BUILD_DEFORMERS = "build_deformers"
BUILD_UTILITY = "build_utility"
BUILD_RIG = "build_rig"
BUILD_EXPORT = "build_export"
BUILD_FULL = "build_full"


class Rig:
    """Rig class."""

    def __init__(self) -> None:
        """Initialize the rig."""
        self.motionModules = {}
        self.deformerModules = {}
        self.utilityModules = {}
        self.exportModules = {}

    def build(self, buildType: str = BUILD_FULL):
        """Build the rig."""
        # TODO: We need to figure out how build order and build type will work together.
        pass
