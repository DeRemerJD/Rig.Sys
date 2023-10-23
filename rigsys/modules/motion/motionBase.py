"""Base class for motion modules."""

import rigsys.modules.moduleBase as moduleBase

import maya.cmds as cmds


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
        # self.moduleRig = None
        self.plugParent = None
        self.worldParent = None

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
    
    def moduleHierarchy(self):
        self.moduleNode = cmds.createNode("transform", n="{}_{}_MODULE".format(self.side, self.label))
        self.moduleUtilities = cmds.createNode("transform", n="{}_{}_utilities".format(self.side, self.label))
        # self.moduleRig = cmds.createNode("transform", "{}_{}_rig".format(self.side, self.label))
        cmds.parent(self.moduleUtilities, self.moduleNode)
        cmds.parent(self.moduleNode, "modules")
        

    # To be called in the module
    def createPlugParent(self, plug=None, position=None, rotation=None):
        plugParent = cmds.createNode("transform", n="{}_{}_plugParent".format(self.side, self.label))
        if plug:
            cmds.xform(plugParent, ws=True, t=cmds.xform(plug, q=True, ws=True, t=True))
            cmds.xform(plugParent, ws=True, ro=cmds.xform(plug, q=True, ws=True, ro=True))
        if position:
            cmds.xform(plugParent, ws=True, t=position)
        if rotation:
            cmds.xform(plugParent, ws=True, ro=rotation)
            
        cmds.parent(plugParent, self.moduleNode)
        return plugParent
    
    # To be called in the module
    def createWorldParent(self):
        worldParent = cmds.createNode("transform", n="{}_{}_worldParent".format(self.side, self.label))
        cmds.parent(worldParent, self.moduleNode)
        return worldParent
