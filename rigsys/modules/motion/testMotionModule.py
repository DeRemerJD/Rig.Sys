"""Test motion module."""


import maya.cmds as cmds

import rigsys.lib.proxy as proxy
import rigsys.modules.motion.motionBase as motionBase


class TestMotionModule(motionBase.MotionModuleBase):
    """Test motion module."""

    def __init__(
        self,
        rig,
        side: str = "",
        label: str = "",
        buildOrder: int = 2000,
        isMuted: bool = False,
        parent: str = None,
        mirror: bool = False,
        selectedPlug: str = "",
        selectedSocket: str = "",
    ) -> None:
        """Initialize the module."""
        super().__init__(
            rig,
            side,
            label,
            buildOrder,
            isMuted,
            parent,
            mirror,
            selectedPlug,
            selectedSocket,
        )

        self.proxies = {
            "Proxy1": proxy.Proxy(
                side=self.side, label=self.label, name="Proxy1", position=[0, 0, 0]
            ),
        }

        self.socket = {
            "SomeSocket": None,
            "AnotherSocket": None,
        }

        self.plug = {
            "SomePlug": None,
            "AnotherPlug": None,
        }

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self):
        """Build the module."""
        rootPar = cmds.createNode("transform", n=self.getFullName() + "_grp")
        rootCtrl = cmds.createNode("transform", n=self.getFullName() + "_CTRL")
        cmds.parent(rootCtrl, rootPar)

        # Create socket nodes
        self.sockets["SomeSocket"] = cmds.createNode(
            "transform", n=self.getFullName() + "_SomeSocket"
        )
        self.sockets["AnotherSocket"] = cmds.createNode(
            "transform", n=self.getFullName() + "_AnotherSocket"
        )

        for socket in self.sockets.values():
            cmds.parent(socket, rootCtrl)

        # Create plug nodes
        self.plugs["SomePlug"] = cmds.createNode(
            "transform", n=self.getFullName() + "_SomePlug"
        )
        self.plugs["AnotherPlug"] = cmds.createNode(
            "transform", n=self.getFullName() + "_AnotherPlug"
        )

        for plug in self.plugs.values():
            cmds.parent(plug, rootCtrl)

        cmds.xform(rootPar, ws=True, t=self.proxies["Proxy1"].position)
        self.parentToRootNode(rootPar)
