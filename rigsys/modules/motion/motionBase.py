"""Base class for motion modules."""


import rigsys.modules.moduleBase as moduleBase

import maya.cmds as cmds


class MotionModuleBase(moduleBase.ModuleBase):
    """Base class for motion modules.

    Attributes:
        - parent: (str) The name of the parent module.
        - _parentObject: (module) The parent module object.
    """

    def __init__(self, rig, name: str = "", side: str = "", label: str = "", buildOrder: int = 2000,
                 isMuted: bool = False, parent: str = None, mirror: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig=rig, name=name, side=side, label=label, buildOrder=buildOrder, isMuted=isMuted,
                         mirror=mirror)

        self.plug: str = ""
        # Key: label, Value: Node
        self.socket: dict = {}

        self.proxies: dict = {}
        self.parent = parent
        self._parentObject = None

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

    def parentToRootNode(self, node):
        """Parent the given node under the rig node."""
        cmds.parent(node, self._rig.rigNode)
