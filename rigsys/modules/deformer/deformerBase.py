"""Base class for deformer modules."""


import rigsys.modules.moduleBase as moduleBase


class DeformerModuleBase(moduleBase.ModuleBase):
    """Base class for deformer modules."""

    def __init__(
        self,
        rig,
        side: str = "",
        label: str = "",
        buildOrder: int = 2000,
        isMuted: bool = False,
        mirror: bool = False,
        bypassProxiesOnly: bool = False,
    ) -> None:
        """Initialize the module."""
        super().__init__(
            rig=rig,
            side=side,
            label=label,
            buildOrder=buildOrder,
            isMuted=isMuted,
            mirror=mirror,
            bypassProxiesOnly=bypassProxiesOnly,
        )
