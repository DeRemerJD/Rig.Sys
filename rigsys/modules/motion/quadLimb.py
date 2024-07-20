"""Quad Limb Motion Module."""

import maya.cmds as cmds

import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.joint as jointTools
import rigsys.lib.proxy as proxy
import rigsys.modules.motion.motionBase as motionBase


class QuadLimb(motionBase.MotionModuleBase):
    """Quad Limb Motion Module"""

    def __init__(
        self,
        rig,
        side="",
        label="",
        ctrlShapes="circle",
        ctrlScale=None,
        addOffset=True,
        clavicle=True,
        buildOrder: int = 2000,
        isMuted: bool = False,
        parent: str = None,
        mirror: bool = False,
        bypassProxiesOnly: bool = True,
        selectedPlug: str = "",
        selectedSocket: str = "",
        aimAxis: str = "+x",
        upAxis: str = "-z",
        pvMultiplier: float = 1.0,
        curvedCalf: bool = True,
        ikCtrlToFloor: bool = True,
        foot: bool = False,
        nameSet: dict = {
            "Root": "Root",
            "Start": "Start",
            "UpMid": "UpMid",
            "LoMid": "LoMid",
            "End": "End",
        },
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
            bypassProxiesOnly,
            selectedPlug,
            selectedSocket,
            aimAxis,
            upAxis,
        )

        self.addOffset = addOffset
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        if self.ctrlScale == None:
            self.ctrlScale = [1.0, 1.0, 1.0]
        self.clavicle = clavicle

        # Module Specific Exposed Variables
        self.pvMultiplier = pvMultiplier
        self.curvedCalf = curvedCalf
        self.nameSet = nameSet
        self.ikCtrlToFloor = (ikCtrlToFloor,)
        self.foot = foot

        self.proxies = {
            self.nameSet["Root"]: proxy.Proxy(
                position=[3, 10, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["Root"],
                plug=True,
            ),
            self.nameSet["Start"]: proxy.Proxy(
                position=[5, 10, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["Start"],
                plug=False,
                parent=self.nameSet["Root"],
            ),
            self.nameSet["UpMid"]: proxy.Proxy(
                position=[5, 5, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["UpMid"],
                parent=self.nameSet["Start"],
            ),
            self.nameSet["LoMid"]: proxy.Proxy(
                position=[5, 3, -1],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["LoMid"],
                parent=self.nameSet["UpMid"],
            ),
        }
        if self.curvedCalf:
            previousParent = None
            for i in range(1, 6):
                if previousParent is None:
                    previousParent = self.nameSet["LoMid"]
                self.proxies[f"{self.nameSet['LoMid']}_{i}"] = proxy.Proxy(
                    position=[5, 3, -1],
                    rotation=[0, 0, 0],
                    side=self.side,
                    label=self.label,
                    name=f"{self.nameSet['LoMid']}_{i}",
                    parent=previousParent,
                )
                previousParent = f"{self.nameSet['LoMid']}_{i}"

            self.proxies[self.nameSet["End"]] = proxy.Proxy(
                position=[5, 1, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["End"],
                parent=previousParent,
            )
        else:
            self.proxies[self.nameSet["End"]] = proxy.Proxy(
                position=[5, 1, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["End"],
                parent=self.nameSet["LoMid"],
            )

        if self.foot:
            self.proxies["Pivot"] = proxy.Proxy(
                position=[5, 1, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Pivot",
                parent=self.nameSet["End"],
            )

            self.proxies["Heel"] = proxy.Proxy(
                position=[5, 1, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Heel",
                parent=self.nameSet["End"],
            )

            self.proxies["OutBank"] = proxy.Proxy(
                position=[5, 1, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="OutBank",
                parent=self.nameSet["End"],
            )

            self.proxies["InBank"] = proxy.Proxy(
                position=[5, 1, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="InBank",
                parent=self.nameSet["End"],
            )

            self.proxies["Ball"] = proxy.Proxy(
                position=[5, 1, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Ball",
                parent="Pivot",
            )

            self.proxies["Toe"] = proxy.Proxy(
                position=[5, 1, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Toe",
                parent="Ball",
            )

            self.proxies["Global"] = proxy.Proxy(
                position=[5, 1, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Global",
                parent=self.nameSet["End"],
            )

        # Module Based Variables
        self.poleVector = None
        self.sockets = {}
        self.plugs = {"Local": None, "World": None}

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self) -> None:
        """Run the module."""

        # # Safety Check
        # if self.numberOfJoints <= 0:
        #     cmds.error(f"Number of joints is less than 0 or 0; default 11: {self.numberOfJoints}")

        plugPosition = self.proxies[self.nameSet["Root"]].position
        plugRotation = self.proxies[self.nameSet["Root"]].rotation
        # MAKE MODULE NODES
        self.moduleHierarchy()

        # Make Plug Transforms
        self.plugParent = self.createPlugParent(
            position=plugPosition, rotation=plugRotation
        )
        self.worldParent = self.createWorldParent()
        self.plugs["Local"] = self.plugParent
        self.plugs["World"] = self.worldParent

        baseJoints, FKJoints, IKJoints, upConnector = self.buildSkeleton()
        (
            IKControls,
            FKControls,
            upRollJoints,
            loRollJoints,
            upIK,
            loIK,
            guideIK,
        ) = self.buildBaseControls(baseJoints, IKJoints, FKJoints, upConnector)
        if self.foot:
            self.buildFoot(
                baseJoints, IKJoints, FKJoints, IKControls, FKControls, upIK, guideIK
            )
        # IKControls, FKControls, midCtrl, endCtrl, upRollJoints, loRollJoints, upIK, loIK = self.buildBaseControls(baseJoints, IKJoints, FKJoints, upConnector)
        # self.buildRibbon(baseJoints, upRollJoints, loRollJoints, midCtrl, endCtrl)

        # Cleanup
        cmds.parent(baseJoints[0], self.moduleUtilities)
        self.addSocketMetaData()

    """
    TODO: Working on the base skeleton. Should be positioned and built correctly? Will move onto
    the controls which were duped from the limb module. Still needs the secondary IK limb
    that drives the orientation of the lower leg.
    """

    def buildSkeleton(self):
        omit = ["Ball", "Toe", "Pivot", "Heel", "InBank", "OutBank", "Global"]
        baseJoints = []
        IKJoints = []
        FKJoints = []
        for key, val in self.proxies.items():
            if key not in omit:
                jnt = cmds.createNode("joint", n=f"{self.side}_{self.label}_{val.name}")
                cmds.xform(jnt, ws=True, t=val.position)
                baseJoints.append(jnt)
                self.sockets[key] = jnt
                if len(baseJoints) == 1:
                    self.bindJoints[jnt] = None
                else:
                    self.bindJoints[jnt] = baseJoints[len(baseJoints) - 2]

        if self.poleVector is None:
            poleVector = cmds.createNode(
                "locator", n=f"{self.side}_{self.label}_PoleVectorShape"
            )
            par = cmds.listRelatives(poleVector, p=True)[0]
            self.poleVector = cmds.rename(par, f"{self.side}_{self.label}_PoleVector")
            pvPar = cmds.createNode("transform", n=f"{self.poleVector}_grp")
            cmds.parent(self.poleVector, pvPar)
            destination = jointTools.getPoleVector(
                baseJoints[1], baseJoints[2], baseJoints[3], self.pvMultiplier
            )
            cmds.xform(pvPar, ws=True, t=destination)

            for i in ["X", "Y", "Z"]:
                cmds.setAttr(f"{self.poleVector}.localScale{i}", 0, l=True)

        index = 1
        for j in baseJoints:
            if j is not baseJoints[0] and j is not baseJoints[1]:
                cmds.parent(j, baseJoints[index])
                index += 1

        # cmds.parent(baseJoints[1], baseJoints[0])
        # cmds.parent(baseJoints[2], baseJoints[1])
        # cmds.parent(baseJoints[3], baseJoints[2])
        # cmds.parent(baseJoints[4], baseJoints[3])

        # jointTools.aim([baseJoints[0]], [baseJoints[1]])
        aimVec = jointTools.axisToVector(self.aimAxis)
        upVec = jointTools.axisToVector(self.upAxis)
        jointTools.aimSequence(
            baseJoints[1::],
            upObj=self.poleVector,
            aimAxis=self.aimAxis,
            upAxis=self.upAxis,
        )
        ac = cmds.aimConstraint(
            baseJoints[1],
            baseJoints[0],
            aim=aimVec,
            u=upVec,
            wut="objectrotation",
            wu=upVec,
            wuo=baseJoints[1],
        )[0]
        cmds.delete(ac)
        cmds.parent(baseJoints[1], baseJoints[0])
        cmds.makeIdentity(baseJoints[0], a=True)

        index = 1
        for jnt in baseJoints[1::]:
            fkJnt = cmds.createNode("joint", n=f"{jnt}_FK")
            ikJnt = cmds.createNode("joint", n=f"{jnt}_IK")

            FKJoints.append(fkJnt)
            IKJoints.append(ikJnt)

            cmds.xform(
                [fkJnt, ikJnt], ws=True, t=cmds.xform(jnt, q=True, ws=True, t=True)
            )
            cmds.xform(
                [fkJnt, ikJnt], ws=True, ro=cmds.xform(jnt, q=True, ws=True, ro=True)
            )
            cmds.makeIdentity([fkJnt, ikJnt], a=True)

            if jnt != baseJoints[1]:
                cmds.parent(fkJnt, f"{baseJoints[index]}_FK")
                cmds.parent(ikJnt, f"{baseJoints[index]}_IK")
                index += 1
            else:
                cmds.parent(fkJnt, baseJoints[0])
                cmds.parent(ikJnt, baseJoints[0])

        socketConnector = cmds.createNode("joint", n=f"{baseJoints[1]}_Connection")
        cmds.xform(
            socketConnector,
            ws=True,
            t=cmds.xform(baseJoints[1], q=True, ws=True, t=True),
        )
        cmds.xform(
            socketConnector,
            ws=True,
            ro=cmds.xform(baseJoints[1], q=True, ws=True, ro=True),
        )

        cmds.parent(socketConnector, baseJoints[0])
        cmds.parent([baseJoints[1], FKJoints[0], IKJoints[0]], socketConnector)
        return baseJoints, FKJoints, IKJoints, socketConnector

    def buildBaseControls(self, baseJoints, IKJoints, FKJoints, socketConnector):
        # Make 3 Point IK for Quad Calc:: Guide Joints / IK

        guideLength_1 = cmds.xform(IKJoints[2], q=True, a=True, t=True)[0]
        if self.curvedCalf:
            guideLength_2 = (
                cmds.xform(IKJoints[1], q=True, a=True, t=True)[0]
                + cmds.xform(IKJoints[3], q=True, a=True, t=True)[0]
                + cmds.xform(IKJoints[4], q=True, a=True, t=True)[0]
                + cmds.xform(IKJoints[5], q=True, a=True, t=True)[0]
                + cmds.xform(IKJoints[6], q=True, a=True, t=True)[0]
                + cmds.xform(IKJoints[7], q=True, a=True, t=True)[0]
            )
        else:
            guideLength_2 = (
                cmds.xform(IKJoints[1], q=True, a=True, t=True)[0]
                + cmds.xform(IKJoints[3], q=True, a=True, t=True)[0]
            )

        # Make joints
        startGuide = cmds.createNode("joint", n=f"{self.side}_{self.label}_StartGuide")
        midGuide = cmds.createNode(
            "joint", n=f"{self.side}_{self.label}_MidGuide", p=startGuide
        )
        endGuide = cmds.createNode(
            "joint", n=f"{self.side}_{self.label}_EndGuide", p=midGuide
        )

        cmds.parent(startGuide, socketConnector)
        # Position joint root
        cmds.xform(
            startGuide, ws=True, t=cmds.xform(IKJoints[0], q=True, ws=True, t=True)
        )
        cmds.xform(
            startGuide, ws=True, ro=cmds.xform(IKJoints[0], q=True, ws=True, ro=True)
        )

        # Add guide lengths to counter pivit guide joints, position them, freeze
        cmds.xform(midGuide, r=True, t=[guideLength_1, 0, 0])
        cmds.xform(endGuide, r=True, t=[guideLength_2, 0, 0])
        cmds.xform(midGuide, r=True, ro=[0, 90, 0])
        cmds.makeIdentity(startGuide, a=True)

        # Generate IK, place IK, constrain
        guideIKHandle = cmds.ikHandle(
            n=f"{self.side}_{self.label}_GuideIK",
            sj=startGuide,
            ee=endGuide,
            sol="ikRPsolver",
            p=1,
        )
        guideEff = cmds.rename(guideIKHandle[1], f"{self.side}_{self.label}_GuideEFF")
        guideIKHandle = guideIKHandle[0]
        cmds.xform(
            guideIKHandle, ws=True, t=cmds.xform(IKJoints[-1], q=True, ws=True, t=True)
        )
        # pvc = cmds.poleVectorConstraint(IKJoints[1], guideIKHandle) Instead PV to the pv control.
        cmds.setAttr(f"{guideIKHandle}.twist", 180)

        # Make controls
        IKControls = []
        FKControls = []
        # IK Control
        ikGrp = cmds.createNode("transform", n=f"{IKJoints[-1]}_grp")
        ikCtrl = cmds.createNode("transform", n=f"{IKJoints[-1]}_CTRL", p=ikGrp)
        cmds.xform(ikGrp, ws=True, t=cmds.xform(IKJoints[-1], q=True, ws=True, t=True))
        if self.ikCtrlToFloor:
            t = cmds.xform(ikGrp, q=True, a=True, t=True)
            cmds.xform(ikGrp, a=True, t=[t[0], 0, t[2]])

            ikCtrlObject = ctrlCrv.Ctrl(
                node=ikCtrl,
                shape="box",
                scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
                offset=[0, self.ctrlScale[1] * 1, 0],
                orient=[0, 0, 0],
            )
        else:
            ikCtrlObject = ctrlCrv.Ctrl(
                node=ikCtrl,
                shape="box",
                scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
                offset=[0, 0, 0],
                orient=[0, 0, 0],
            )
        ikCtrlObject.giveCtrlShape()
        IKControls.append(ikCtrl)

        ikOffsetGrp = cmds.createNode(
            "transform", n=f"{IKJoints[-1]}_Offset_grp", p=ikCtrl
        )
        ikOffsetCtrl = cmds.createNode(
            "transform", n=f"{IKJoints[-1]}_Offset_CTRL", p=ikOffsetGrp
        )

        cmds.xform(
            ikOffsetGrp, ws=True, t=cmds.xform(IKJoints[-1], q=True, ws=True, t=True)
        )

        IKControls.append(ikOffsetCtrl)

        ikCtrlObject = ctrlCrv.Ctrl(
            node=ikOffsetCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
            offset=[0, 0, 0],
            orient=[0, 0, 0],
        )
        ikCtrlObject.giveCtrlShape()

        # Pole Vector Control
        pvCtrl = cmds.createNode("transform", n=f"{self.poleVector}_CTRL")
        cmds.xform(
            pvCtrl, ws=True, t=cmds.xform(self.poleVector, q=True, ws=True, t=True)
        )
        pvPar = cmds.listRelatives(self.poleVector, p=True)[0]
        cmds.parent(pvCtrl, pvPar)
        cmds.parent(self.poleVector, pvCtrl)
        pvCtrlObject = ctrlCrv.Ctrl(
            node=pvCtrl,
            shape="sphere",
            scale=[
                self.ctrlScale[0] * 0.75,
                self.ctrlScale[1] * 0.75,
                self.ctrlScale[2] * 0.75,
            ],
            offset=[0, 0, 0],
        )
        pvCtrlObject.giveCtrlShape()
        IKControls.append(pvCtrl)

        if self.curvedCalf:
            cmds.parent(pvPar, ikCtrl)

        # Make IK Handle
        ikRP = cmds.ikHandle(
            n=f"{self.side}_{self.label}_UP_IK",
            sj=IKJoints[0],
            ee=IKJoints[2],
            sol="ikRPsolver",
            p=1,
        )
        effRP = cmds.rename(ikRP[1], f"{self.side}_{self.label}_UP_EFF")
        ikRP = ikRP[0]
        # cmds.parent(ik, ikCtrl) Needs parenting to the calf IK
        oc = cmds.orientConstraint(ikCtrl, IKJoints[-1], n=f"{IKJoints}_oc", mo=1)
        pvc = cmds.poleVectorConstraint(self.poleVector, ikRP, n=f"{ikRP}_pvc")
        pvc = cmds.poleVectorConstraint(
            self.poleVector, guideIKHandle, n=f"{guideIKHandle}_pvc"
        )

        ikSC = cmds.ikHandle(
            n=f"{self.side}_{self.label}_LO_IK",
            sj=IKJoints[2],
            ee=IKJoints[-1],
            sol="ikSCsolver",
            p=1,
        )
        effSC = cmds.rename(ikSC[1], f"{self.side}_{self.label}_LO_EFF")
        ikSC = ikSC[0]
        # pvc = cmds.poleVectorConstraint(IKJoints[1], ikSC, n=f"{ikSC}_pvc")

        # Add calf logic
        oc = cmds.orientConstraint(midGuide, ikOffsetGrp, n=f"{ikOffsetGrp}_oc", mo=0)
        cmds.parent([ikRP, ikSC], ikOffsetCtrl)
        cmds.parent(guideIKHandle, ikCtrl)

        # FK Controls
        for jnt in FKJoints:
            grp = cmds.createNode("transform", n=f"{jnt}_grp")
            ctrl = cmds.createNode("transform", n=f"{jnt}_CTRL", p=grp)
            cmds.xform(grp, ws=True, t=cmds.xform(jnt, q=True, ws=True, t=True))
            cmds.xform(grp, ws=True, ro=cmds.xform(jnt, q=True, ws=True, ro=True))
            fkCtrlObject = ctrlCrv.Ctrl(
                node=ctrl,
                shape="square",
                scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
                offset=[0, 0, 0],
                orient=[0, 0, 90],
            )
            fkCtrlObject.giveCtrlShape()
            ptc = cmds.parentConstraint(ctrl, jnt, n=f"{jnt}_ptc", mo=0)

            if len(FKControls) != 0:
                cmds.parent(grp, FKControls[-1])
            FKControls.append(ctrl)

        # Clavicle Control
        clavGrp = cmds.createNode("transform", n=f"{baseJoints[0]}_grp")
        clavCtrl = cmds.createNode("transform", n=f"{baseJoints[0]}_CTRL", p=clavGrp)
        clavCtrlObject = ctrlCrv.Ctrl(
            node=clavCtrl,
            shape="sphere",
            scale=[
                self.ctrlScale[0] * 1.5,
                self.ctrlScale[1] * 1.5,
                self.ctrlScale[2] * 1.5,
            ],
            offset=[0, 0, 0],
        )
        clavCtrlObject.giveCtrlShape()
        cmds.xform(
            clavGrp, ws=True, t=cmds.xform(baseJoints[0], q=True, ws=True, t=True)
        )
        cmds.xform(
            clavGrp, ws=True, ro=cmds.xform(baseJoints[0], q=True, ws=True, ro=True)
        )

        ptc = cmds.parentConstraint(
            clavCtrl, baseJoints[0], n=f"{baseJoints[0]}_ptc", mo=0
        )
        fkPar = cmds.listRelatives(FKControls[0], p=True)[0]

        # Shoulder Orientation Global / Local
        globalTransform = cmds.createNode("transform", n=f"{baseJoints[1]}_Global")
        localTransform = cmds.createNode("transform", n=f"{baseJoints[1]}_Local")

        cmds.xform(
            globalTransform,
            ws=True,
            t=cmds.xform(baseJoints[1], q=True, ws=True, t=True),
        )
        cmds.xform(
            globalTransform,
            ws=True,
            ro=cmds.xform(baseJoints[1], q=True, ws=True, ro=True),
        )
        cmds.xform(
            localTransform,
            ws=True,
            t=cmds.xform(baseJoints[1], q=True, ws=True, t=True),
        )
        cmds.xform(
            localTransform,
            ws=True,
            ro=cmds.xform(baseJoints[1], q=True, ws=True, ro=True),
        )

        cmds.parent(globalTransform, self.worldParent)
        cmds.parent(localTransform, clavCtrl)

        ptc = cmds.parentConstraint(
            clavCtrl, globalTransform, n=f"{globalTransform}_ptc", mo=1
        )
        oc = cmds.orientConstraint(
            [globalTransform, localTransform], fkPar, n=f"{fkPar}_Lock_oc", mo=0
        )[0]
        cmds.setAttr(f"{oc}.interpType", 2)
        pc = cmds.pointConstraint(localTransform, fkPar, n=f"{fkPar}_Lock_pc", mo=0)

        upT = cmds.createNode(
            "transform", n=f"{self.side}_{self.label}_upPV", p=clavCtrl
        )
        cmds.xform(upT, ws=True, t=cmds.xform(clavCtrl, q=True, ws=True, t=True))
        cmds.xform(upT, ws=True, ro=cmds.xform(clavCtrl, q=True, ws=True, ro=True))
        loT = cmds.createNode("transform", n=f"{self.side}_{self.label}_loPV", p=ikCtrl)
        cmds.xform(loT, ws=True, t=cmds.xform(ikCtrl, q=True, ws=True, t=True))
        cmds.xform(loT, ws=True, ro=cmds.xform(ikCtrl, q=True, ws=True, ro=True))
        pc = cmds.pointConstraint([upT, loT], pvPar, n=f"{pvPar}_pc", mo=1)

        # Connections.
        cmds.addAttr(ikCtrl, ln="IK_FK_Switch", at="float", min=0, max=1, dv=0, k=1)

        index = 0
        for jnt in baseJoints[1::]:
            bc = cmds.createNode("blendColors", n=f"{jnt}_bc")

            cmds.connectAttr(f"{ikCtrl}.IK_FK_Switch", f"{bc}.blender")
            cmds.connectAttr(f"{FKJoints[index]}.rotate", f"{bc}.color1")
            cmds.connectAttr(f"{IKJoints[index]}.rotate", f"{bc}.color2")
            cmds.connectAttr(f"{bc}.output", f"{jnt}.rotate")

            index += 1
        fkCtrlPar = cmds.listRelatives(FKControls[0], p=True)[0]
        cmds.connectAttr(f"{ikCtrl}.IK_FK_Switch", f"{fkCtrlPar}.visibility")
        rev = cmds.createNode("reverse", n=f"{self.side}_{self.label}_IKFK_rev")
        cmds.connectAttr(f"{ikCtrl}.IK_FK_Switch", f"{rev}.input.inputX")
        cmds.connectAttr(f"{rev}.output.outputX", f"{ikGrp}.visibility")
        cmds.connectAttr(f"{rev}.output.outputX", f"{pvPar}.visibility")
        for ctrl in FKControls:
            cmds.addAttr(
                ctrl,
                ln="IK_FK_Switch",
                proxy=f"{ikCtrl}.IK_FK_Switch",
                at="float",
                min=0,
                max=1,
                dv=0,
                k=1,
            )
        cmds.addAttr(
            pvCtrl,
            ln="IK_FK_Switch",
            proxy=f"{ikCtrl}.IK_FK_Switch",
            at="float",
            min=0,
            max=1,
            dv=0,
            k=1,
        )

        upRollJoints, loRollJoints, upIK, loIK = self.buildCounterJoints(
            baseJoints, socketConnector
        )

        upGrps = []
        upControls = []
        # Create Up Roll Ctrls / joints
        for i in range(3):
            name = f"{upRollJoints[0]}_{i}"
            grp = cmds.createNode("transform", n=f"{name}_grp")
            ctrl = cmds.createNode("transform", n=f"{name}_CTRL", p=grp)
            jnt = cmds.createNode("joint", n=f"{name}", p=ctrl)

            ctrlOject = ctrlCrv.Ctrl(
                node=ctrl,
                shape="circle",
                scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
                offset=[0, 0, 0],
                orient=[0, 90, 0],
            )
            ctrlOject.giveCtrlShape()

            upGrps.append(grp)
            upControls.append(ctrl)
            self.sockets[name] = jnt
            self.bindJoints[jnt] = baseJoints[1]

        loGrps = []
        loControls = []
        loJoints = []
        # Create Up Roll Ctrls / joints
        if self.curvedCalf:
            index = 0
            for i in baseJoints[4:-1]:
                name = f"{loRollJoints[0]}_{index}"
                grp = cmds.createNode("transform", n=f"{name}_grp")
                ctrl = cmds.createNode("transform", n=f"{name}_CTRL", p=grp)
                jnt = cmds.createNode("joint", n=f"{name}", p=ctrl)
                ctrlOject = ctrlCrv.Ctrl(
                    node=ctrl,
                    shape="circle",
                    scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
                    offset=[0, 0, 0],
                    orient=[0, 90, 0],
                )
                ctrlOject.giveCtrlShape()

                loGrps.append(grp)
                loControls.append(ctrl)
                loJoints.append(jnt)
                self.sockets[name] = jnt
                if len(loJoints) == 1:
                    self.bindJoints[jnt] = baseJoints[3]
                else:
                    self.bindJoints[jnt] = loJoints[len(loJoints) - 2]

                index += 1
        else:
            for i in range(3):
                name = f"{loRollJoints[0]}_{i}"
                grp = cmds.createNode("transform", n=f"{name}_grp")
                ctrl = cmds.createNode("transform", n=f"{name}_CTRL", p=grp)
                jnt = cmds.createNode("joint", n=f"{name}", p=ctrl)

                ctrlOject = ctrlCrv.Ctrl(
                    node=ctrl,
                    shape="circle",
                    scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
                    offset=[0, 0, 0],
                    orient=[0, 90, 0],
                )
                ctrlOject.giveCtrlShape()

                loGrps.append(grp)
                loControls.append(ctrl)
                self.sockets[name] = jnt
                self.bindJoints[jnt] = baseJoints[3]

        # Constrain up and lo controls
        ptc = cmds.parentConstraint(
            [upRollJoints[0], upRollJoints[1]], upGrps[0], n=f"{upGrps[0]}_ptc", mo=0
        )[0]
        cmds.setAttr(f"{ptc}.interpType", 2)
        cmds.setAttr(f"{ptc}.{upRollJoints[0]}W0", 3)
        cmds.setAttr(f"{ptc}.{upRollJoints[1]}W1", 1)

        ptc = cmds.parentConstraint(
            [upRollJoints[0], upRollJoints[1]], upGrps[1], n=f"{upGrps[1]}_ptc", mo=0
        )[0]
        cmds.setAttr(f"{ptc}.interpType", 2)
        cmds.setAttr(f"{ptc}.{upRollJoints[0]}W0", 1)
        cmds.setAttr(f"{ptc}.{upRollJoints[1]}W1", 1)

        ptc = cmds.parentConstraint(
            [upRollJoints[0], upRollJoints[1]], upGrps[2], n=f"{upGrps[2]}_ptc", mo=0
        )[0]
        cmds.setAttr(f"{ptc}.interpType", 2)
        cmds.setAttr(f"{ptc}.{upRollJoints[0]}W0", 1)
        cmds.setAttr(f"{ptc}.{upRollJoints[1]}W1", 3)

        if self.curvedCalf:
            index = 0
            for i in baseJoints[4:-1]:
                ptc = cmds.parentConstraint(
                    i, loGrps[index], n=f"{loGrps[index]}_ptc", mo=0
                )
                index += 1
        else:
            ptc = cmds.parentConstraint(
                [loRollJoints[0], loRollJoints[1]],
                loGrps[0],
                n=f"{loGrps[0]}_ptc",
                mo=0,
            )[0]
            cmds.setAttr(f"{ptc}.interpType", 2)
            cmds.setAttr(f"{ptc}.{loRollJoints[0]}W0", 1)
            cmds.setAttr(f"{ptc}.{loRollJoints[1]}W1", 3)

            ptc = cmds.parentConstraint(
                [loRollJoints[0], loRollJoints[1]],
                loGrps[1],
                n=f"{loGrps[1]}_ptc",
                mo=0,
            )[0]
            cmds.setAttr(f"{ptc}.interpType", 2)
            cmds.setAttr(f"{ptc}.{loRollJoints[0]}W0", 1)
            cmds.setAttr(f"{ptc}.{loRollJoints[1]}W1", 1)

            ptc = cmds.parentConstraint(
                [loRollJoints[0], loRollJoints[1]],
                loGrps[2],
                n=f"{loGrps[2]}_ptc",
                mo=0,
            )[0]
            cmds.setAttr(f"{ptc}.interpType", 2)
            cmds.setAttr(f"{ptc}.{loRollJoints[0]}W0", 3)
            cmds.setAttr(f"{ptc}.{loRollJoints[1]}W1", 1)

        # Cleanup
        if self.curvedCalf:
            cmds.parent(
                [clavGrp, cmds.listRelatives(FKControls[0], p=True)[0]], self.plugParent
            )
        else:
            cmds.parent(
                [clavGrp, pvPar, cmds.listRelatives(FKControls[0], p=True)[0]],
                self.plugParent,
            )
        cmds.parent(ikGrp, self.worldParent)

        cmds.parent(loGrps, self.plugParent)
        cmds.parent(upGrps, self.plugParent)

        return (
            IKControls,
            FKControls,
            upRollJoints,
            loRollJoints,
            upIK,
            loIK,
            guideIKHandle,
        )

    def buildCounterJoints(self, baseJoints, socketConnector):
        upRollStart = cmds.createNode("joint", n=f"{baseJoints[1]}_Roll")
        upRollEnd = cmds.createNode("joint", n=f"{baseJoints[1]}_End", p=upRollStart)
        cmds.xform(
            upRollStart, ws=True, t=cmds.xform(baseJoints[1], q=True, ws=True, t=True)
        )
        cmds.xform(
            upRollStart, ws=True, ro=cmds.xform(baseJoints[1], q=True, ws=True, ro=True)
        )
        cmds.xform(
            upRollEnd, ws=True, t=cmds.xform(baseJoints[2], q=True, ws=True, t=True)
        )
        cmds.makeIdentity(upRollStart, a=True)
        cmds.parent(upRollStart, socketConnector)
        upIK = cmds.ikHandle(
            n=f"{upRollStart}_IK", sj=upRollStart, ee=upRollEnd, sol="ikSCsolver", p=4
        )
        upEff = upIK[1]
        upEff = cmds.rename(upEff, upIK[0].replace("IK", "EFF"))
        upIK = upIK[0]
        pc = cmds.pointConstraint(baseJoints[2], upIK, n=f"{upIK}_pc", mo=0)
        oc = cmds.orientConstraint(baseJoints[1], upRollEnd, n=f"{upRollEnd}_oc", mo=0)
        cmds.parent(upIK, socketConnector)

        loRollStart = cmds.createNode("joint", n=f"{baseJoints[-1]}_Roll")
        loRollEnd = cmds.createNode("joint", n=f"{baseJoints[-1]}_End", p=loRollStart)
        cmds.xform(
            loRollStart, ws=True, t=cmds.xform(baseJoints[-1], q=True, ws=True, t=True)
        )
        cmds.xform(
            loRollStart,
            ws=True,
            ro=cmds.xform(baseJoints[-1], q=True, ws=True, ro=True),
        )
        cmds.xform(
            loRollEnd, ws=True, t=cmds.xform(baseJoints[3], q=True, ws=True, t=True)
        )
        cmds.makeIdentity(loRollStart, a=True)
        cmds.parent(loRollStart, baseJoints[4])
        loIK = cmds.ikHandle(
            n=f"{loRollStart}_IK", sj=loRollStart, ee=loRollEnd, sol="ikSCsolver", p=4
        )
        loEff = loIK[1]
        loEff = cmds.rename(loEff, loIK[0].replace("IK", "EFF"))
        loIK = loIK[0]
        pc = cmds.pointConstraint(baseJoints[3], loIK, n=f"{loIK}_pc", mo=0)
        oc = cmds.orientConstraint(baseJoints[3], loRollEnd, n=f"{loRollEnd}_oc", mo=0)
        cmds.parent(loIK, baseJoints[-1])
        # return [upRollStart, upRollEnd], [midRollStart, midRollEnd], [loRollStart, loRollEnd], upIK, midIK, loIK

        return [upRollStart, upRollEnd], [loRollStart, loRollEnd], upIK, loIK

    def buildFoot(
        self, baseJoints, IKJoints, FKJoints, IKControls, FKControls, upIK, guideIK
    ):
        # for key, val in self.proxies.items():
        #     if key in omit:
        #         jnt = cmds.createNode("joint", n=f"{self.side}_{self.label}_{val.name}")
        label = f"{self.side}_{self.label}"
        base = []
        ik = []
        fk = []
        index = 0
        for i in ["", "_IK", "_FK"]:
            ball = cmds.createNode("joint", n=f"{label}_{self.proxies['Ball'].name}{i}")
            toe = cmds.createNode(
                "joint", n=f"{label}_{self.proxies['Toe'].name}{i}", p=ball
            )
            cmds.xform(ball, ws=True, t=self.proxies["Ball"].position)
            cmds.xform(toe, ws=True, t=self.proxies["Toe"].position)
            if index == 0:
                cmds.parent(ball, baseJoints[-1])
                base.append(ball)
                base.append(toe)
            if index == 1:
                cmds.parent(ball, IKJoints[-1])
                ik.append(ball)
                ik.append(toe)
            if index == 2:
                cmds.parent(ball, FKJoints[-1])
                fk.append(ball)
                fk.append(toe)
            jointTools.aimSequence(
                base, upObj=self.poleVector, aimAxis=self.aimAxis, upAxis=self.upAxis
            )
            jointTools.aimSequence(
                ik, upObj=self.poleVector, aimAxis=self.aimAxis, upAxis=self.upAxis
            )
            jointTools.aimSequence(
                fk, upObj=self.poleVector, aimAxis=self.aimAxis, upAxis=self.upAxis
            )
            index += 1
            cmds.makeIdentity([ball, toe], a=True)

        inverse = [
            "InBank",
            "OutBank",
            "Heel",
            "Pivot",
            "Toe",
            "Ball",
            self.nameSet["End"],
        ]
        iJnts = []
        index = 0
        for i in inverse:
            jnt = cmds.createNode("joint", n=f"{label}_{i}_INV")

            if len(iJnts) > 0:
                cmds.parent(jnt, iJnts[index - 1])

            cmds.xform(jnt, ws=True, t=self.proxies[i].position)
            iJnts.append(jnt)
            index += 1
            self.sockets[i] = jnt
            if len(iJnts) == 1:
                self.bindJoints[jnt] = baseJoints[-1]
            else:
                self.bindJoints[jnt] = iJnts[len(iJnts) - 2]

        ballIK = cmds.ikHandle(
            sj=IKJoints[-1], ee=ik[0], n=f"{ik[0]}_IK", sol="ikSCsolver"
        )
        ballEFF = ballIK[1]
        ballIK = ballIK[0]
        toeIK = cmds.ikHandle(sj=ik[0], ee=ik[1], n=f"{ik[1]}_IK", sol="ikSCsolver")
        toeEFF = toeIK[1]
        toeIK = toeIK[0]

        globalGrp = cmds.createNode(
            "transform", n=f"{label}_{self.proxies['Global'].name}_grp"
        )
        globalCtrl = cmds.createNode(
            "transform", n=f"{label}_{self.proxies['Global'].name}_CTRL", p=globalGrp
        )

        globalCtrlObject = ctrlCrv.Ctrl(
            node=globalCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
            offset=[0, 0, 0],
        )
        globalCtrlObject.giveCtrlShape()

        cmds.xform(
            globalGrp,
            ws=True,
            t=cmds.xform(
                f"{label}_{self.proxies['Global'].name}_proxy", q=True, ws=True, t=True
            ),
        )

        rollMD = cmds.createNode("multiplyDivide", n=f"{label}_InvToe_md")
        raiseCD = cmds.createNode("condition", n=f"{label}_InvRaise_cd")
        bankCD = cmds.createNode("condition", n=f"{label}_InvBank_cd")

        for i in [raiseCD, bankCD]:
            cmds.setAttr(f"{i}.colorIfFalseR", 0)
            cmds.setAttr(f"{i}.colorIfFalseG", 0)
            cmds.setAttr(f"{i}.colorIfFalseB", 0)

        for i in ["X", "Y", "Z"]:
            if i != "X":
                cmds.setAttr(f"{rollMD}.input2{i}", -1)
            else:
                cmds.setAttr(f"{rollMD}.input2{i}", 1)

        cmds.setAttr(f"{bankCD}.operation", 2)
        cmds.setAttr(f"{raiseCD}.operation", 4)

        cmds.connectAttr(f"{globalCtrl}.translateZ", f"{rollMD}.input1X")
        cmds.connectAttr(f"{globalCtrl}.rotateZ", f"{bankCD}.colorIfTrueR")
        cmds.connectAttr(f"{globalCtrl}.rotateZ", f"{bankCD}.colorIfFalseG")
        cmds.connectAttr(f"{globalCtrl}.rotateZ", f"{bankCD}.firstTerm")
        cmds.connectAttr(f"{globalCtrl}.rotateX", f"{raiseCD}.colorIfTrueR")
        cmds.connectAttr(f"{globalCtrl}.rotateX", f"{raiseCD}.colorIfFalseG")
        cmds.connectAttr(f"{globalCtrl}.rotateX", f"{raiseCD}.firstTerm")
        # ["InBank", "OutBank", "Heel", "Pivot", "Toe", "Ball", self.nameSet["End"]]
        cmds.connectAttr(f"{bankCD}.outColorR", f"{iJnts[0]}.rotateZ")
        cmds.connectAttr(f"{bankCD}.outColorG", f"{iJnts[1]}.rotateZ")
        cmds.connectAttr(f"{raiseCD}.outColorR", f"{iJnts[2]}.rotateX")
        cmds.connectAttr(f"{raiseCD}.outColorG", f"{iJnts[5]}.rotateX")
        cmds.connectAttr(f"{rollMD}.outputX", f"{iJnts[4]}.rotateX")
        cmds.connectAttr(f"{globalCtrl}.rotateY", f"{iJnts[3]}.rotateY")

        cmds.addAttr(globalCtrl, ln="heelPivot", at="float", dv=0, k=True)
        cmds.connectAttr(f"{globalCtrl}.heelPivot", f"{iJnts[2]}.rotateY")
        fkGrps = []
        fkCtrls = []
        # FK Jazz
        for jnt in fk:
            if jnt == fk[0]:
                grp = cmds.createNode("transform", n=f"{jnt}_FK_grp", p=FKControls[-1])
                ctrl = cmds.createNode("transform", n=f"{jnt}_FK_CTRL", p=grp)
            else:
                grp = cmds.createNode("transform", n=f"{jnt}_FK_grp", p=FKControls[-1])
                ctrl = cmds.createNode("transform", n=f"{jnt}_FK_CTRL", p=fkGrps[0])
            cmds.xform(grp, ws=True, m=cmds.xform(jnt, q=True, ws=True, m=True))
            fkGrps.append(grp)
            fkCtrls.append(ctrl)
            fkCtrlObject = ctrlCrv.Ctrl(
                node=ctrl,
                shape="square",
                scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
                offset=[0, 0, 0],
                orient=[0, 0, 90],
            )
            fkCtrlObject.giveCtrlShape()
            ptc = cmds.parentConstraint(ctrl, jnt, n=f"{jnt}_ptc", mo=0)

        # Parent inverse and IKs
        cmds.parent(f"{iJnts[0]}", f"{IKControls[0]}")
        cmds.parent(f"{guideIK}", f"{iJnts[-1]}")
        cmds.parent(f"{ballIK}", f"{iJnts[-2]}")
        cmds.parent(f"{toeIK}", f"{iJnts[-3]}")
        cmds.parent(globalGrp, IKControls[0])

        pc = cmds.pointConstraint(
            iJnts[-1], cmds.listRelatives(IKControls[1], p=True)[0]
        )

        for index in range(2):
            bc = cmds.createNode("blendColors", n=f"{base[index]}_bc")
            cmds.connectAttr(f"{IKControls[0]}.IK_FK_Switch", f"{bc}.blender")
            cmds.connectAttr(f"{fk[index]}.rotate", f"{bc}.color1")
            cmds.connectAttr(f"{ik[index]}.rotate", f"{bc}.color2")
            cmds.connectAttr(f"{bc}.output", f"{base[index]}.rotate")

        cmds.setAttr(f"{iJnts[0]}.visibility", False)
