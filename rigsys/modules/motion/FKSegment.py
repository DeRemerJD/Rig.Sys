"""FK / Reverse FK Motion Module."""


import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy

import maya.cmds as cmds


class FKSegment(motionBase.MotionModuleBase):
    """Root Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, addOffset=True, segments=1,
                 reverse=True, buildOrder: int = 2000, isMuted: bool = False, parent: str = None, 
                 mirror: bool = False, selectedPlug: str = "", selectedParentSocket: str = "") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, parent, mirror, selectedPlug, selectedParentSocket)

        if ctrlScale is None:
            ctrlScale = [1.0, 1.0, 1.0]

        self.addOffset = addOffset
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        self.segments = segments
        self.reverse = reverse

        self.proxies = {
            "Start": proxy.Proxy(
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Start"
            ),
            "End": proxy.Proxy(
                position=[0, 10, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="End",
                parent="Start"
            ),
            "UpVector": proxy.Proxy(
                position=[0, 0, -10],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="UpVector",
                parent="Start"
            )
        }
        if self.segments > 1:
            par = "Start"
            for i in range(1, self.segments):
                self.proxies[str(i)] = proxy.Proxy(
                    position=[0, 0, 0],
                    rotation=[0, 0, 0],
                    side=self.side,
                    label=self.label,
                    name=str(i),
                    parent=par
                )
                par = str(i)
                if i == self.segments:
                    self.proxies["End"].parent = str(i)

        self.socket = {
            "Start": None,
            "End": None
        }
        if self.segments > 1:
            for i in range(1, self.segments):
                self.socket[str(i)] = None

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self) -> None:
        """Run the module."""
        plugPosition = self.proxies["Start"].position
        plugRotation = self.proxies["Start"].rotation
        # MAKE MODULE NODES
        self.moduleHierarchy()

        # Make Plug Transforms
        self.plugParent = self.createPlugParent(
            position=plugPosition, rotation=plugRotation
        )
        self.worldParent = self.createWorldParent()

        FKCtrls = []
        FKGrps = []
        ### MODULE STRUCTURE ###
        for key, proxy in self.proxies.items():
            if key is not "UpVector" or key is not "End":
                grp = cmds.createNode("transform", n="{}_{}_grp".format(
                    self.getFullName(), self.proxies[key].name))
                ctrl = cmds.createNode("transform", n="{}_{}_CTRL".format(
                    self.getFullName(), self.proxies[key].name))
                
                cmds.parent(ctrl, grp)
                FKCtrls.append(ctrl)
                FKGrps.append(grp)
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

        cmds.xform(rootPar, ws=True, t=proxyPosition)
        cmds.xform(rootPar, ws=True, ro=proxyRotation)
        cmds.parent(rootPar, self.worldParent)

        
        self.socket["Base"] = rootJnt
        if self.addOffset:
            self.socket["Offset"] = offsetJnt
        print(self.socket)
