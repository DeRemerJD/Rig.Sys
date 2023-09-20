"""Base class for utility modules."""


import rigsys.modules.moduleBase as moduleBase


class UtilityModuleBase(moduleBase.ModuleBase):
    """Base class for utility modules."""

    def __init__(self) -> None:
        """Initialize the module."""
        super().__init__()
        self.buildOrder = 3000
