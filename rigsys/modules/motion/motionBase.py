"""Base class for motion modules."""
import maya.cmds as cmds


import rigsys.modules.moduleBase as moduleBase


class MotionModuleBase(moduleBase.ModuleBase):
    """Base class for motion modules."""

    def __init__(self, rig, name: str = "", side: str = "", label: str = "", buildOrder: int = 2000, isMuted: bool = False,
                 parent: str = None, mirror: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig=rig, name=name, side=side, label=label, buildOrder=buildOrder, isMuted=isMuted, mirror=mirror)

        self.plug: dict = {}
        # Key: label, Value: Node
        self.socket: dict = {}

        self.proxies: dict = {}
        self.parent = parent
        self._parentObject = None

        # Module Based Constructors
        self.moduleNode = None
        self.moduleUtilies = None
        self.moduleRig = None

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
    
    def moduleHierarchy(self):
        self.moduleNode = cmds.createNode("transform", "{}_{}_MODULE".format(self.side, self.label))
        self.moduleUtilities = cmds.createNode("transform", "{}_{}_utilities".format(self.side, self.label))
        self.moduleRig = cmds.createNode("transform", "{}_{}_rig".format(self.side, self.label))

        cmds.parent([self.moduleUtilies, self.moduleRig], self.moduleNode)

    # To be called in the module
    def createPlugParent(self, plug):
        plugParent = cmds.createNode("transform", n="{}_{}_plugParent".format(self.side, self.labe))
        cmds.xform(plugParent, ws=True, t=cmds.xform(plug, q=True, ws=True, t=True))
        cmds.xform(plugParent, ws=True, ro=cmds.xform(plug, q=True, ws=True, ro=True))
        cmds.parent(plugParent, self.moduleRig)
        return plugParent
    
    # To be called in the module
    def createWorldParent(self):
        worldParent = cmds.createNode("transform", n="{}_{}_worldParent".format(self.side, self.labe))
        cmds.parent(worldParent, self.moduleRig)
        return worldParent
