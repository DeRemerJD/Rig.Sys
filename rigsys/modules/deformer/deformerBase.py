"""Base class for deformer modules."""


import rigsys.modules.moduleBase as moduleBase


class DeformerModuleBase(moduleBase.ModuleBase):
    """Base class for deformer modules."""

    def __init__(self) -> None:
        """Initialize the module."""
        super().__init__()
        self.buildOrder = 2000
