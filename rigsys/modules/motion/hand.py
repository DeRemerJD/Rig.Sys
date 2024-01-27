"""FK Motion Module."""

import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds


class FK(motionBase.MotionModuleBase):
    """FK Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, addOffset=True, meta: bool = True,
                 thumb: bool = True, numberOfFingers: int = 4, numberOfFingerJoints: int = 4, numberOfThumbJoints: int = 3,
                 buildOrder: int = 2000, isMuted: bool = False, parent: str = None,
                 mirror: bool = False, selectedPlug: str = "", selectedSocket: str = "") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, parent, mirror, selectedPlug, selectedSocket)

        self.addOffset = addOffset
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        self.meta = meta
        self.thumb = thumb
        self.numOfFingers = numberOfFingers
        self.numOfFingerJoints = numberOfFingerJoints
        self.numOfThumbJoints = numberOfThumbJoints

        self.proxies = {
            "Root": proxy.Proxy(
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Root",
                plug=True
            ),
            "End": proxy.Proxy(
                position=[0, 0, -10],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="End",
                parent="Root"
            ),
            "UpVector": proxy.Proxy(
                position=[0, 0, -10],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="UpVector",
                parent="Root"
            ),
            "Global": proxy.Proxy(
                position=[0, 0, -10],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Global",
                parent="Root"
            ),
        } 

        for i in range(self.numOfFingers):
            for j in range(self.numOfFingerJoints):
                name = f"Finger{i}_{j}"
                if j == 0:
                    par = "Root"
                else:
                    par = f"{i}_{j-1}"   
                self.proxies[name] = proxy.Proxy(
                    position=[0, 0, 0],
                    rotation=[0, 0, 0],
                    side=self.side,
                    label=self.label,
                    name=str(i),
                    parent=par
                )

        if self.thumb:
            for j in range(self.numOfThumbJoints):
                name = f"Thumb_{j}"
                if j == 0:
                    par = "Root"
                else:
                    par = f"{i}_{j-1}"   
                self.proxies[name] = proxy.Proxy(
                    position=[0, 0, 0],
                    rotation=[0, 0, 0],
                    side=self.side,
                    label=self.label,
                    name=str(i),
                    parent=par
                )


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

    def buildModule(self):
        """Run the module."""

        plugPosition = self.proxies["Root"].position
        plugRotation = self.proxies["Root"].rotation
        # MAKE MODULE NODES
        self.moduleHierarchy()

        # Make Plug Transforms
        self.plugParent = self.createPlugParent(
            position=plugPosition, rotation=plugRotation
        )
        self.worldParent = self.createWorldParent()

        excluded = []
        for key in self.proxies.keys():
            if "UpVector" in key:
                excluded.append(key)
            if "End" in key:
                excluded.append(key)
            if "Global" in key:
                excluded.append(key)

        Joints = []
        # Make joints
        for key, val in self.proxies.items():
            if key not in excluded:
                name = f"{self.side}_{self.label}_{val.name}"
                jnt = cmds.createNode("joint", n=f"{self.side}")

        index = 0
        for fJnt in FKJoints:
            if fJnt != FKJoints[-1]:
                cmds.parent(FKJoints[index + 1], fJnt)
            index += 1

        jointTools.aimSequence(
            FKJoints, aimAxis="+x", upAxis="-z",
            upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy")
        
        FKGrps = []
        FKCtrls = []
        for fJnt in FKJoints:
            grp = cmds.createNode("transform", n=f"{fJnt}_grp")
            ctrl = cmds.createNode("transform", n=f"{fJnt}_CTRL")
            cmds.parent(ctrl, grp)

            cmds.xform(grp, ws=True, t=cmds.xform(
                fJnt, q=True, ws=True, t=True
            ))
            cmds.xform(grp, ws=True, ro=cmds.xform(
                fJnt, q=True, ws=True, ro=True
            ))

            FKGrps.append(grp)
            FKCtrls.append(ctrl)

            if self.addOffset:
                oGrp = cmds.createNode("transform", n=f"{fJnt}_grp")
                oCtrl = cmds.createNode("transform", n=f"{fJnt}_CTRL")
                cmds.parent(oCtrl, oGrp)

                cmds.xform(grp, ws=True, t=cmds.xform(
                    fJnt, q=True, ws=True, t=True
                ))
                cmds.xform(grp, ws=True, ro=cmds.xform(
                    fJnt, q=True, ws=True, ro=True
                ))

                cmds.parent(oGrp, ctrl)

                ptc = cmds.parentConstraint(ctrl, fJnt, n=f"{fJnt}_ptc", mo=0)[0]
                cmds.setAttr(f"{ptc}.interpType", 2)
                sc = cmds.scaleConstraint(ctrl, fJnt, n=f"{fJnt}_sc", mo=0)
            else:
                ptc = cmds.parentConstraint(ctrl, fJnt, n=f"{fJnt}_ptc", mo=0)[0]
                cmds.setAttr(f"{ptc}.interpType", 2)
                sc = cmds.scaleConstraint(ctrl, fJnt, n=f"{fJnt}_sc", mo=0)