"""Base class for motion modules."""

import logging

import rigsys.modules.moduleBase as moduleBase

import maya.cmds as cmds

logger = logging.getLogger(__name__)


class MotionModuleBase(moduleBase.ModuleBase):
    """Base class for motion modules."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 2000,
                 isMuted: bool = False, parent: str = None, mirror: bool = False,
                 bypassProxiesOnly: bool = True, selectedPlug: str = "", selectedSocket: str = "",
                 aimAxis: str = "+x", upAxis: str = "-z") -> None:
        """Initialize the module."""
        super().__init__(rig=rig, side=side, label=label, buildOrder=buildOrder, isMuted=isMuted,
                         mirror=mirror, bypassProxiesOnly=bypassProxiesOnly)

        self.proxies: dict = {}
        self.bypassProxiesOnly = bypassProxiesOnly

        # Key: label, Value: Node
        self.plugs: dict = {}
        self.sockets: dict = {}

        self.bindJoints: dict = {}

        self.selectedPlug = selectedPlug
        self.selectedSocket = selectedSocket

        self.parent = parent
        self._parentObject = None

        # Module Based Constructors
        self.moduleNode = None
        self.moduleUtilities = None
        self.plugParent = None
        self.worldParent = None
        self.aimAxis = aimAxis
        self.upAxis = upAxis

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
        cmds.setAttr(f"{self.moduleUtilities}.visibility", 0)

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

    def socketPlugParenting(self):
        if self.parent is not None:
            socket = cmds.getAttr(f"{self.parent}_MODULE.{self.selectedSocket}", asString=True)
        self.selectedPlug = self.plugParent

        ptc = cmds.parentConstraint(socket, self.selectedPlug, mo=1)[0]
        cmds.setAttr(f"{ptc}.interpType", 2)
        sc = cmds.scaleConstraint(socket, self.selectedPlug, mo=1)

    def addSocketMetaData(self):
        cmds.addAttr(self.moduleNode, ln="SocketData", at="enum", en="--------")
        for key, val in self.sockets.items():
            cmds.addAttr(self.moduleNode, ln=key, at="enum", en=str(val))
