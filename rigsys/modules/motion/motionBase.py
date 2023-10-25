"""Base class for motion modules."""

import logging

import rigsys.modules.moduleBase as moduleBase

import maya.cmds as cmds

logger = logging.getLogger(__name__)


class MotionModuleBase(moduleBase.ModuleBase):
    """Base class for motion modules."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 2000,
                 isMuted: bool = False, parent: str = None, mirror: bool = False,
                 selectedPlug: str = "", selectedParentSocket: str = "") -> None:
        """Initialize the module."""
        super().__init__(rig=rig, side=side, label=label, buildOrder=buildOrder, isMuted=isMuted,
                         mirror=mirror)

        self.proxies: dict = {}

        # Key: label, Value: Node
        self.plugs: dict = {}
        self.sockets: dict = {}

        self.selectedPlug = selectedPlug
        self.selectedParentSocket = selectedParentSocket

        self.parent = parent
        self._parentObject = None

        # Module Based Constructors
        self.moduleNode = None
        self.moduleUtilities = None
        self.plugParent = None
        self.worldParent = None

    def run(self, buildProxiesOnly: bool = False, usedSavedProxyData: bool = True, proxyData: dict = {}) -> None:
        """Run the module."""
        if usedSavedProxyData:
            try:
                moduleProxyData = proxyData[self.getFullName()]

                for proxyKey, proxyTransformationData in moduleProxyData.items():
                    self.proxies[proxyKey].position = proxyTransformationData["position"]
                    self.proxies[proxyKey].rotation = proxyTransformationData["rotation"]

            except KeyError:
                logger.error(f"Proxy data for module {self.getFullName()} not found.")

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
        """Create the module hierarchy."""
        self.moduleNode = cmds.createNode("transform", n="{}_{}_MODULE".format(self.side, self.label))
        self.moduleUtilities = cmds.createNode("transform", n="{}_{}_utilities".format(self.side, self.label))
        # self.moduleRig = cmds.createNode("transform", "{}_{}_rig".format(self.side, self.label))
        cmds.parent(self.moduleUtilities, self.moduleNode)
        cmds.parent(self.moduleNode, "modules")

    def createPlugParent(self, plug=None, position=None, rotation=None):
        """Create a plug parent for the module."""
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

    def createWorldParent(self):
        """Create a world parent for the module."""
        worldParent = cmds.createNode("transform", n="{}_{}_worldParent".format(self.side, self.label))
        cmds.parent(worldParent, self.moduleNode)
        return worldParent
