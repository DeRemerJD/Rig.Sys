"""FK Motion Module."""


import rigsys.modules.motion.motionBase as motionBase


class FK(motionBase.MotionModuleBase):
    """FK Motion Module."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the module."""
        super().__init__(args, kwargs)

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self):
        """Run the module."""
        return super().buildModule()
