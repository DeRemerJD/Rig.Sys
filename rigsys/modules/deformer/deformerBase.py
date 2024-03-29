"""Base class for deformer modules."""


import rigsys.modules.moduleBase as moduleBase


class DeformerModuleBase(moduleBase.ModuleBase):
    """Base class for deformer modules."""

    def __init__(self, rig, label: str = "", buildOrder: int = 2000,
                 isMuted: bool = False, mirror: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig=rig, label=label, buildOrder=buildOrder, isMuted=isMuted, mirror=mirror)
