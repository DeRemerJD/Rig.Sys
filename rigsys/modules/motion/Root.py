"""World Root Motion Module."""


import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy

import maya.cmds as cmds


class Root(motionBase.MotionModuleBase):
    """Root Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, addOffset=True,
                 buildOrder: int = 2000, isMuted: bool = False, parent: str = None, mirror: bool = False,
                 selectedPlug: str = "", selectedParentSocket: str = "") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, parent, mirror, selectedPlug, selectedParentSocket)

        if ctrlScale is None:
            ctrlScale = [1.0, 1.0, 1.0]

        self.addOffset = addOffset
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale

        self.proxies = {
            "Root": proxy.Proxy(
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Base",
            )
        }

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self) -> None:
        """Run the module."""
        print("DEBUGGING. . .")
        print(self.side)
        print(self.label)
        print(self.ctrlShapes)
        print(self.ctrlScale)
        print(self.addOffset)

        # Get Proxy pos / rot values
        proxyPosition = self.proxies["Root"].position
        proxyRotation = self.proxies["Root"].rotation

        # MAKE MODULE NODES
        self.moduleHierarchy()

        # Make Plug Transforms
        self.plugParent = self.createPlugParent(
            position=proxyPosition, rotation=proxyRotation
        )
        self.worldParent = self.createWorldParent()

        # Structure
        rootPar = cmds.createNode("transform", n=self.getFullName() + "_grp")
        rootCtrl = cmds.createNode("transform", n=self.getFullName() + "_CTRL")
        cmds.parent(rootCtrl, rootPar)
        rootCtrlObj = ctrlCrv.Ctrl(
            node=rootCtrl,
            shape=self.ctrlShapes,
            scale=self.ctrlScale,
            orient=[90, 0, 0],
        )
        rootCtrlObj.giveCtrlShape()
        if self.addOffset:
            offsetPar = cmds.createNode(
                "transform", n=self.getFullName() + "Offset_grp"
            )
            offsetCtrl = cmds.createNode(
                "transform", n=self.getFullName() + "Offset_CTRL"
            )
            cmds.parent(offsetCtrl, offsetPar)
            cmds.parent(offsetPar, rootCtrl)
            offsetScale = []
            for x in self.ctrlScale:
                offsetScale.append(x * 0.75)
            offsetCtrlObj = ctrlCrv.Ctrl(
                node=offsetCtrl,
                shape=self.ctrlShapes,
                scale=offsetScale,
                orient=[90, 0, 0],
            )
            offsetCtrlObj.giveCtrlShape()

        cmds.xform(rootPar, ws=True, t=proxyPosition)
        cmds.xform(rootPar, ws=True, ro=proxyRotation)
        cmds.parent(rootPar, self.worldParent)
