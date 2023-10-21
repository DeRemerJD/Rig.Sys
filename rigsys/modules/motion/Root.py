"""World Root Motion Module."""


import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy

import maya.cmds as cmds


class Root(motionBase.MotionModuleBase):
    """Root Motion Module."""

    def __init__(self, *args, ctrlShapes="circle", ctrlScale=[1.0, 1.0, 1.0], addOffset=True, **kwargs) -> None:
        """Initialize the module."""
        super().__init__(args, kwargs)
        self.addOffset = addOffset
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale

        self.proxies = {
            "Root": proxy.Proxy(position=[0, 0, 0], rotation=[0, 0, 0], side="M", label="Root")
        }

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self) -> None:
        """Run the module."""
        # Build overall structure
        proxyPosition = self.proxies["Root"].position
        # Checking if the vars are carrying over.
        cmds.createNode('transform', n=self.side + "_" + self.label)

        # Structure
        rootPar = cmds.createNode("transform", n=self.getFullName() + "_grp")
        rootCtrl = cmds.createNode("transform", n=self.getFullName() + "_CTRL")
        cmds.parent(rootCtrl, rootPar)
        rootCtrlObj = ctrlCrv.Ctrl(
            node=rootCtrl, shape=self.ctrlShapes, scale=self.ctrlScale
            )
        rootCtrlObj.giveCtrlShape()
        if self.addOffset:
            offsetPar = cmds.createNode(
                "transform", n=self.getFullName() + "_grp"
            )
            offsetCtrl = cmds.createNode(
                "transform", n=self.getFullName() + "_CTRL"
            )
            cmds.parent(offsetCtrl, offsetPar)
            cmds.parent(offsetPar, rootCtrl)
            offsetScale = []
            for x in self.ctrlScale:
                offsetScale.append(x*.75)
            offsetCtrlObj = ctrlCrv.Ctrl(
                node=offsetCtrl, shape=self.ctrlShapes, scale=offsetScale
                )
            offsetCtrlObj.giveCtrlShape()
        cmds.xform(rootPar, ws=True, t=proxyPosition)
