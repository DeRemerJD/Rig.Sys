"""Test motion module."""


import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.proxy as proxy

import maya.cmds as cmds


class TestMotionModule(motionBase.MotionModuleBase):
    """Test motion module."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 2000,
                 isMuted: bool = False, parent: str = None, mirror: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, parent, mirror)

        self.proxies = {
            "Proxy1": proxy.Proxy(
                side=self.side,
                label=self.label,
                name="Proxy1",
                position=[0, 0, 0]
            ),
        }

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self):
        """Build the module."""
        rootPar = cmds.createNode("transform", n=self.getFullName() + "_grp")
        rootCtrl = cmds.createNode("transform", n=self.getFullName() + "_CTRL")
        cmds.parent(rootCtrl, rootPar)

        cmds.xform(rootPar, ws=True, t=self.proxies["Proxy1"].position)
        self.parentToRootNode(rootPar)
