"""Base class for motion modules."""


import rigsys.modules.moduleBase as moduleBase


class MotionModuleBase(moduleBase.ModuleBase):
    """Base class for motion modules."""

    def __init__(self, rig, name: str = "", side: str = "", label: str = "", buildOrder: int = 2000, isMuted: bool = False,
                 parent: str = None, mirror: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig=rig, name=name, side=side, label=label, buildOrder=buildOrder, isMuted=isMuted, mirror=mirror)

        self.plug: str = ""
        # Key: label, Value: Node
        self.socket: dict = {}

        print("Before self.proxies declaration")
        print(self.proxies)
        # self.proxies: dict = {}
        print("After self.proxies declaration")
        print(self.proxies)
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
        for proxy in self.proxies.values():
            proxy.build()

    def buildModule(self):
        """Build the rest of the module."""
        pass

    def doMirror(self):
        """Mirror the module."""
        # TODO: Implement mirror
        return super().doMirror()
