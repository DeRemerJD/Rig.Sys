"""Base class for utility modules."""


import rigsys.modules.moduleBase as moduleBase


class UtilityModuleBase(moduleBase.ModuleBase):
    """Base class for utility modules."""

    def __init__(self, rig, name: str = "", buildOrder: int = 3000, isMuted: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig=rig, name=name, buildOrder=buildOrder, isMuted=isMuted)
