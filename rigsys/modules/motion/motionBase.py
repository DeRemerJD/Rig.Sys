"""Base class for motion modules."""


import rigsys.modules.moduleBase as moduleBase


class MotionModuleBase(moduleBase.ModuleBase):
    """Base class for motion modules."""

    def __init__(self, rig, name: str = "", buildOrder: int = 2000, isMuted: bool = False,
                 parent: str = None) -> None:
        """Initialize the module."""
        super().__init__(rig=rig, name=name, buildOrder=buildOrder, isMuted=isMuted)

        self.plug: str = ""
        self.socket: dict = {}

        self.parent = parent
        self._parentObject = None

        if self.parent is not None:
            self._rig.setParent(self, self.parent)

    def run(self, buildProxiesOnly: bool = False):
        """Run the module."""
        # Build proxy step
        self.buildProxies()

        if buildProxiesOnly:
            return

        # Build module step
        self.buildModule()

    def buildProxies(self):
        """Build the proxies for the module."""
        pass

    def buildModule(self):
        """Build the rest of the module."""
        pass
