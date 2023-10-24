"""Build bind joints utility module."""


import rigsys.modules.utility.utilityBase as utilityBase


class BindJoints(utilityBase.UtilityModuleBase):
    """Build bind joints utility module."""

    def __init__(self, rig, label: str = "", buildOrder: int = 3000, isMuted: bool = False,
                 mirror: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig, label, buildOrder, isMuted, mirror)

    def run(self) -> None:
        """Run the module."""
        # TODO: Implement
        pass
