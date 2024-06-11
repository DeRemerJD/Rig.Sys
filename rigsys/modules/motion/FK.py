"""FK Motion Module."""

import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds


class FK(motionBase.MotionModuleBase):
    """FK Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, addOffsets=True, segments=5,
                 buildOrder: int = 2000, isMuted: bool = False, parent: str = None,
                 mirror: bool = False, bypassProxiesOnly: bool = True, selectedPlug: str = "", selectedSocket: str = "",
                 aimAxis: str = "+x", upAxis: str = "-z") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, 
                         parent, mirror, bypassProxiesOnly, selectedPlug, 
                         selectedSocket, aimAxis, upAxis)

        self.addOffsets = addOffsets
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        if self.ctrlScale == None:
            self.ctrlScale = [1.0, 1.0, 1.0]
        self.segments = segments

        self.proxies = {
            "Start": proxy.Proxy(
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Start",
                plug=True
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
            self.proxies["End"] = self.proxies.pop("End")

            self.proxies["End"].parent = str(segments - 1)

        self.sockets = {
            "Start": None
        }

        if self.segments > 1:
            for i in range(1, self.segments):
                self.sockets[f"Segment_{i}"] = None

        self.plugs = {
            "Local": None,
            "World": None
        }

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self):
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
        self.plugs["Local"] = self.plugParent
        self.plugs["World"] = self.worldParent

        FKJoints = []
        # Make joints
        for key, val in self.proxies.items():
            if key != "End" and key != "UpVector":
                fJnt = cmds.createNode("joint", n=f"{self.getFullName()}_{val.name}")
                FKJoints.append(fJnt)
                cmds.xform(fJnt, ws=True, t=val.position)
                if key != "Start":
                    self.sockets[f"Segment_{key}"] = fJnt
                else:
                    self.sockets["Start"] = fJnt

                if len(FKJoints) == 1:
                    self.bindJoints[fJnt] = None
                else:
                    self.bindJoints[fJnt] = FKJoints[len(FKJoints) - 2]

        index = 0
        for fJnt in FKJoints:
            if fJnt != FKJoints[-1]:
                cmds.parent(FKJoints[index + 1], fJnt)
            index += 1

        jointTools.aimSequence(
            FKJoints, aimAxis=self.aimAxis, upAxis=self.upAxis,
            upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy")

        FKGrps = []
        FKCtrls = []
        index = 0
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
            ctrlObject = ctrlCrv.Ctrl(
                    node=ctrl,
                    shape="circle",
                    scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
                    offset=[0, 0, 0],
                    orient=[0, 90, 0]
                )
            ctrlObject.giveCtrlShape()

            if self.addOffsets:
                oGrps = []
                oCtrls = []
                oGrp = cmds.createNode("transform", n=f"{fJnt}_grp")
                oCtrl = cmds.createNode("transform", n=f"{fJnt}_CTRL")
                ctrlObject = ctrlCrv.Ctrl(
                    node=ctrl,
                    shape="square",
                    scale=[self.ctrlScale[0]*0.85, self.ctrlScale[1]*0.85, self.ctrlScale[2]*0.85],
                    offset=[0, 0, 0],
                    orient=[0, 90, 0]
                )
                ctrlObject.giveCtrlShape()

                oGrps.append(oGrp)
                oCtrls.append(oCtrl)
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
        if self.addOffsets:
            for og in oGrps:
                        cmds.parent(og, FKCtrls[index])
                        index+=1        
            index = 0
        for fg in FKGrps:
            if fg != FKGrps[-1]:
                cmds.parent(FKGrps[index+1], FKCtrls[index])
                index+=1

        cmds.parent([FKGrps[0], FKJoints[0]], self.plugParent)
        self.addSocketMetaData()
