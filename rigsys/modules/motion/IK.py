"""IK Motion Module."""


import rigsys.modules.motion.motionBase as motionBase


class IK(motionBase.MotionModuleBase):
    """IK Motion Module."""

    def __init__(
        self,
        rig,
        side: str = "",
        label: str = "",
        buildOrder: int = 2000,
        isMuted: bool = False,
        parent: str = None,
        mirror: bool = False,
    ) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, parent, mirror)

    def run(self) -> None:
        """Run the module."""
        # TODO: Implement
        pass
