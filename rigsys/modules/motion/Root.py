"""World Root Motion Module."""


import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy

import maya.cmds as cmds


class Root(motionBase.MotionModuleBase):
    """Root Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, addOffset=True,
                 buildOrder: int = 2000, isMuted: bool = False, parent: str = None, mirror: bool = False,
                 bypassProxiesOnly: bool = True, selectedPlug: str = "", selectedSocket: str = "",
                 aimAxis: str = "+x", upAxis: str = "-z") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, 
                         parent, mirror, bypassProxiesOnly, selectedPlug, 
                         selectedSocket, aimAxis, upAxis)

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

        self.sockets = {
            "Base": None
        }
        self.plugs = {
            "Local": None,
            "World": None
        }

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self) -> None:
        """Run the module."""

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
        self.plugs["Local"] = self.plugParent
        self.plugs["World"] = self.worldParent

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
        rootJnt = cmds.createNode(
            "joint", n="{}_{}_{}".format(self.side, self.label, self.proxies["Root"].name)
        )
        cmds.parent(rootJnt, rootCtrl)
        self.sockets["Base"] = rootJnt
        self.bindJoints[rootJnt] = None
        if self.addOffset:
            offsetPar = cmds.createNode(
                "transform", n=self.getFullName() + "Offset_grp"
            )
            offsetCtrl = cmds.createNode(
                "transform", n=self.getFullName() + "Offset_CTRL"
            )
            offsetJnt = cmds.createNode(
                "joint", n="{}_{}_Offset".format(self.side, self.label)
            )
            cmds.parent(offsetJnt, offsetCtrl)
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
            self.sockets["Offset"] = offsetJnt
            self.bindJoints[offsetJnt] = rootJnt

        cmds.xform(rootPar, ws=True, t=proxyPosition)
        cmds.xform(rootPar, ws=True, ro=proxyRotation)
        if self.parent == "" or self.parent is None:
            cmds.parent(rootPar, self.worldParent)
        else:
            cmds.parent(rootPar, self.plugParent)

        self.addSocketMetaData()
