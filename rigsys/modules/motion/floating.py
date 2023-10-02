"""Floating Motion Module."""


import rigsys.modules.motion.motionBase as motionBase


class Floating(motionBase.MotionModuleBase):
    """Floating Motion Module."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the module."""
        super().__init__(args, kwargs)

    def run(self) -> None:
        """Run the module."""
        # TODO: Implement
        pass
