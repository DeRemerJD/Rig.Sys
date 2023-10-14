"""Base class for utility modules."""


import rigsys.modules.moduleBase as moduleBase


class UtilityModuleBase(moduleBase.ModuleBase):
    """Base class for utility modules."""

    def __init__(self, rig, name: str = "", label: str = "", buildOrder: int = 3000, isMuted: bool = False,
                 mirror: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig=rig, name=name, label=label, buildOrder=buildOrder, isMuted=isMuted, mirror=mirror)

    def doMirror(self):
        """Mirror the module."""
        # TODO: Implement mirror
        return super().doMirror()
