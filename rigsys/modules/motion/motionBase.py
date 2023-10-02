"""Base class for motion modules."""


import rigsys.modules.moduleBase as moduleBase


class MotionModuleBase(moduleBase.ModuleBase):
    """Base class for motion modules."""

    def __init__(self, rig, name: str = "", buildOrder: int = 0, isMuted: bool = False,
                 parent: str = None) -> None:
        """Initialize the module."""
        super().__init__(rig=rig, name=name, buildOrder=buildOrder, isMuted=isMuted)
        self.buildOrder = 2000

        self.plug: str = ""
        self.socket: dict = {}

        self.parent = parent
        self._parentObject = None

        if self.parent is not None:
            self._rig.setParent(self, self.parent)
