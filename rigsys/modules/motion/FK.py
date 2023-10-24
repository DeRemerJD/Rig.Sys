"""FK Motion Module."""


import rigsys.modules.motion.motionBase as motionBase


class FK(motionBase.MotionModuleBase):
    """FK Motion Module."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 2000,
                 isMuted: bool = False, parent: str = None, mirror: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, parent, mirror)

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self):
        """Run the module."""
        return super().buildModule()
