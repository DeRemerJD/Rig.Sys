"""FK Motion Module."""


import rigsys.modules.motion.motionBase as motionBase


class FK(motionBase.MotionModuleBase):
    """FK Motion Module."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the module."""
        super().__init__(args, kwargs)

    def buildProxies(self):
        return super().buildProxies()

    def buildModule(self):
        return super().buildModule()
