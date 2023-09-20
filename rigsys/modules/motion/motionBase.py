"""Base class for motion modules."""


import rigsys.modules.moduleBase as moduleBase


class MotionModuleBase(moduleBase.ModuleBase):
    """Base class for motion modules."""

    def __init__(self) -> None:
        """Initialize the module."""
        super().__init__()
        self.buildOrder = 2000
