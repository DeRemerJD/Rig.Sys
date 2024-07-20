"""Proxy class for rigsys modules."""

import copy
import logging

import maya.cmds as cmds

logger = logging.getLogger(__name__)


class Proxy:
    """Proxy class for rigsys modules."""

    def __init__(
        self,
        side="M",
        label="",
        name="",
        parent=None,
        upVector=False,
        position=None,
        rotation=None,
        plug=False,
    ) -> None:
        """Initialize the proxy."""
        if position is None:
            position = [0.0, 0.0, 0.0]
        if rotation is None:
            rotation = [0.0, 0.0, 0.0]

        self.position = position
        self.rotation = rotation
        self.side = side
        self.label = label
        self.name = name
        self.parent = parent
        self.upVector = upVector
        self.plug = plug
        self.proxyModuleNode = None

    def getFullName(self):
        """Return the full name of the proxy."""
        return f"{self.side}_{self.label}"

    def doMirror(self):
        """Mirror the proxy, returning a new proxy object."""
        if self.side == "M":
            logger.error(f"Cannot mirror middle proxy {self.getFullName()}")
            return None

        newProxy = copy.deepcopy(self)

        if self.side == "L":
            newProxy.side = "R"
        elif self.side == "R":
            newProxy.side = "L"

        # Transform data
        newProxy.position[0] *= -1
        newProxy.rotation[0] *= -1
        newProxy.rotation[1] *= -1
        newProxy.rotation[2] *= -1

        return newProxy

    def build(self):
        """Build the proxy."""
        if self.proxyModuleNode is None:
            self.buildProxyModule()
        prx = cmds.createNode(
            "joint", n="{}_{}_{}_proxy".format(self.side, self.label, self.name)
        )
        cmds.parent(prx, self.proxyModuleNode)

        cmds.xform(prx, ws=True, t=self.position, ro=self.rotation)
        if self.parent:
            parent = "{}_{}_{}_proxy".format(self.side, self.label, self.parent)
            cmds.parent(prx, parent)
        # if self.plug:
        #     proxyModule = cmds.createNode("transform", n="{}_{}_proxyMODULE".format(self.side, self.label))
        #     cmds.parent(proxyModule, "proxies")

    def buildProxyModule(self):
        if cmds.objExists("{}_{}_proxyMODULE".format(self.side, self.label)):
            self.proxyModuleNode = "{}_{}_proxyMODULE".format(self.side, self.label)
        else:
            self.proxyModuleNode = cmds.createNode(
                "transform", n="{}_{}_proxyMODULE".format(self.side, self.label)
            )
            cmds.parent(self.proxyModuleNode, "proxies")
