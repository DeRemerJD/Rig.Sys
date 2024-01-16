"""Quad Limb Motion Module."""

import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds

class QuadLimb(motionBase.MotionModuleBase):
    """Quad Limb Motion Module"""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, addOffset=True, clavicle=True,
                 buildOrder: int = 2000, isMuted: bool = False, parent: str = None, 
                 mirror: bool = False, selectedPlug: str = "", selectedSocket: str = "",
                 pvMultiplier: float = 1.0, numberOfJoints: int = 11, 
                 nameSet: dict = {"Root":"Root", "Start":"Start", "UpMid":"UpMid", "LoMid":"LoMid", "End":"End"}) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, parent, mirror, selectedPlug, selectedSocket)

        self.addOffset = addOffset
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        if self.ctrlScale == None:
            self.ctrlScale = [1.0, 1.0, 1.0]
        self.clavicle = clavicle

        # Module Specific Exposed Variables
        self.pvMultiplier = pvMultiplier
        self.numberOfJoints = numberOfJoints
        self.nameSet = nameSet

        self.proxies = {
            self.nameSet["Root"]: proxy.Proxy(
                position=[3, 10, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["Root"],
                plug=True
            ),
            self.nameSet["Start"]: proxy.Proxy(
                position=[5, 10, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["Start"],
                plug=False,
                parent=self.nameSet["Root"]
            ),
            self.nameSet["UpMid"]: proxy.Proxy(
                position=[5, 5, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["UpMid"],
                parent=self.nameSet["Start"]
            ),
            self.nameSet["LoMid"]: proxy.Proxy(
                position=[5, 3, -1],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["LoMid"],
                parent=self.nameSet["UpMid"]
            ),
            self.nameSet["End"]: proxy.Proxy(
                position=[5, 1, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["End"],
                parent=self.nameSet["LoMid"]
            )
        }

        # Module Based Variables
        self.poleVector = None

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()
    
    def buildModule(self) -> None:
        """Run the module."""

        # Safety Check
        if self.numberOfJoints <= 0:
            cmds.error(f"Number of joints is less than 0 or 0; default 11: {self.numberOfJoints}")

        plugPosition = self.proxies[self.nameSet["Root"]].position
        plugRotation = self.proxies[self.nameSet["Root"]].rotation
        # MAKE MODULE NODES
        self.moduleHierarchy()

        # Make Plug Transforms
        self.plugParent = self.createPlugParent(
            position=plugPosition, rotation=plugRotation
        )
        self.worldParent = self.createWorldParent()

        baseJoints, FKJoints, IKJoints, upConnector = self.buildSkeleton()
        # IKControls, FKControls, midCtrl, endCtrl, upRollJoints, loRollJoints, upIK, loIK = self.buildBaseControls(baseJoints, IKJoints, FKJoints, upConnector)
        # self.buildRibbon(baseJoints, upRollJoints, loRollJoints, midCtrl, endCtrl)

        # Cleanup
        cmds.parent(baseJoints[0], self.moduleUtilities)

    '''
    TODO: Working on the base skeleton. Should be positioned and built correctly? Will move onto 
    the controls which were duped from the limb module. Still needs the secondary IK limb 
    that drives the orientation of the lower leg.
    '''
    def buildSkeleton(self):
        baseJoints = []
        IKJoints = []
        FKJoints = []
        for key, val in self.proxies.items():
            jnt = cmds.createNode("joint", n=f"{self.side}_{self.label}_{val.name}")
            cmds.xform(jnt, ws=True, t=val.position)
            baseJoints.append(jnt)

        if self.poleVector is None:
            poleVector = cmds.createNode("locator", n=f"{self.side}_{self.label}_PoleVectorShape")
            par = cmds.listRelatives(poleVector, p=True)[0]
            self.poleVector = cmds.rename(par, f"{self.side}_{self.label}_PoleVector")
            pvPar = cmds.createNode('transform', n=f"{self.poleVector}_grp")
            cmds.parent(self.poleVector, pvPar)
            destination = jointTools.getPoleVector(baseJoints[1], baseJoints[2], baseJoints[3], self.pvMultiplier)
            cmds.xform(pvPar, ws=True, t=destination)
            
            for i in ["X", "Y", "Z"]:
                cmds.setAttr(f"{self.poleVector}.localScale{i}", 0, l=True)

        cmds.parent(baseJoints[1], baseJoints[0])
        cmds.parent(baseJoints[2], baseJoints[1])
        cmds.parent(baseJoints[3], baseJoints[2])
        cmds.parent(baseJoints[4], baseJoints[3])

        # jointTools.aim([baseJoints[0]], [baseJoints[1]])
        jointTools.aimSequence([baseJoints[1], baseJoints[2], baseJoints[3], baseJoints[4]], upObj=self.poleVector)
        cmds.makeIdentity(baseJoints[0], a=True)

        index = 1
        for jnt in baseJoints[1::]:
            fkJnt = cmds.createNode("joint", n=f"{jnt}_FK")
            ikJnt = cmds.createNode("joint", n=f"{jnt}_IK")
            
            FKJoints.append(fkJnt)
            IKJoints.append(ikJnt)

            cmds.xform([fkJnt, ikJnt], ws=True, t=cmds.xform(
                jnt, q=True, ws=True, t=True
            ))
            cmds.xform([fkJnt, ikJnt], ws=True, ro=cmds.xform(
                jnt, q=True, ws=True, ro=True
            ))
            cmds.makeIdentity([fkJnt, ikJnt], a=True)
            
            if jnt != baseJoints[1]:
                cmds.parent(fkJnt, f"{baseJoints[index]}_FK")
                cmds.parent(ikJnt, f"{baseJoints[index]}_IK")
                index+=1
            else:
                cmds.parent(fkJnt, baseJoints[0])
                cmds.parent(ikJnt, baseJoints[0])
            
        socketConnector = cmds.createNode("joint", n=f"{baseJoints[1]}_Connection")
        cmds.xform(socketConnector, ws=True, t=cmds.xform(
            baseJoints[1], q=True, ws=True, t=True
        ))
        cmds.xform(socketConnector, ws=True, ro=cmds.xform(
            baseJoints[1], q=True, ws=True, ro=True
        ))

        cmds.parent(socketConnector, baseJoints[0])
        cmds.parent([baseJoints[1], FKJoints[0], IKJoints[0]], socketConnector)
        return baseJoints, FKJoints, IKJoints, socketConnector
    
    def buildBaseControls(self, baseJoints, IKJoints, FKJoints, socketConnector):
        # Make controls
        IKControls = []
        FKControls = []
        # IK Control
        ikGrp = cmds.createNode('transform', n=f"{IKJoints[2]}_grp")
        ikCtrl = cmds.createNode('transform', n=f"{IKJoints[2]}_CTRL", p=ikGrp)
        cmds.xform(ikGrp, ws=True, t=cmds.xform(
            IKJoints[2], q=True, ws=True, t=True
        ))
        ikCtrlObject = ctrlCrv.Ctrl(
            node=ikCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
            offset=[0, 0, 0],
            orient=[0, 0, 0]
        )
        ikCtrlObject.giveCtrlShape()
        IKControls.append(ikCtrl)

        # Pole Vector Control
        pvCtrl = cmds.createNode('transform', n=f"{self.poleVector}_CTRL")
        cmds.xform(pvCtrl, ws=True, t=cmds.xform(
            self.poleVector, q=True, ws=True, t=True
        ))
        pvPar = cmds.listRelatives(self.poleVector, p=True)[0]
        cmds.parent(pvCtrl, pvPar)
        cmds.parent(self.poleVector, pvCtrl)
        pvCtrlObject = ctrlCrv.Ctrl(
            node=pvCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0]*0.75, self.ctrlScale[1]*0.75, self.ctrlScale[2]*0.75],
            offset=[0, 0, 0]
        )
        pvCtrlObject.giveCtrlShape()
        IKControls.append(pvCtrl)
        
        # Make IK Handle
        ik = cmds.ikHandle(n=f"{self.side}_{self.label}_IK", sj=IKJoints[0], ee=IKJoints[2], sol="ikRPsolver", p=1)
        eff = cmds.rename(ik[1], f"{self.side}_{self.label}_EFF")
        ik = ik[0]
        cmds.parent(ik, ikCtrl)
        oc = cmds.orientConstraint(ikCtrl, IKJoints[2], n=f"{IKJoints}_oc", mo=1)
        pvc = cmds.poleVectorConstraint(self.poleVector, ik, n=f"{ik}_pvc")

        sik = cmds.ikHandle(f"{self.side}")

        # FK Controls
        for jnt in FKJoints:
            grp = cmds.createNode("transform", n=f"{jnt}_grp")
            ctrl = cmds.createNode("transform", n=f"{jnt}_CTRL", p=grp)
            cmds.xform(grp, ws=True, t=cmds.xform(
                jnt, q=True, ws=True, t=True
            ))
            cmds.xform(grp, ws=True, ro=cmds.xform(
                jnt, q=True, ws=True, ro=True
            ))
            fkCtrlObject = ctrlCrv.Ctrl(
                node=ctrl,
                shape="square",
                scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
                offset=[0, 0, 0],
                orient=[0, 0, 90]
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
            scale=[self.ctrlScale[0]*1.5, self.ctrlScale[1]*1.5, self.ctrlScale[2]*1.5],
            offset=[0, 0, 0]
        )
        clavCtrlObject.giveCtrlShape()
        cmds.xform(clavGrp, ws=True, t=cmds.xform(
                baseJoints[0], q=True, ws=True, t=True
            ))
        cmds.xform(clavGrp, ws=True, ro=cmds.xform(
                baseJoints[0], q=True, ws=True, ro=True
            ))
        
        ptc = cmds.parentConstraint(clavCtrl, baseJoints[0], n=f"{baseJoints[0]}_ptc", mo=0)
        fkPar = cmds.listRelatives(FKControls[0], p=True)[0]

        # Shoulder Orientation Global / Local
        globalTransform = cmds.createNode('transform', n=f"{baseJoints[1]}_Global")
        localTransform = cmds.createNode('transform', n=f"{baseJoints[1]}_Local")

        cmds.xform(globalTransform, ws=True, t=cmds.xform(
                baseJoints[1], q=True, ws=True, t=True
            ))
        cmds.xform(globalTransform, ws=True, ro=cmds.xform(
                baseJoints[1], q=True, ws=True, ro=True
            ))
        cmds.xform(localTransform, ws=True, t=cmds.xform(
                baseJoints[1], q=True, ws=True, t=True
            ))
        cmds.xform(localTransform, ws=True, ro=cmds.xform(
                baseJoints[1], q=True, ws=True, ro=True
            ))

        cmds.parent(globalTransform, self.worldParent)
        cmds.parent(localTransform, clavCtrl)
        
        ptc = cmds.parentConstraint(clavCtrl, globalTransform, n=f"{globalTransform}_ptc", mo=1)
        oc = cmds.orientConstraint([globalTransform, localTransform], fkPar, n=f"{fkPar}_Lock_oc", mo=0)[0]
        cmds.setAttr(f"{oc}.interpType", 2)
        pc = cmds.pointConstraint(localTransform, fkPar, n=f"{fkPar}_Lock_pc", mo=0)

        upT = cmds.createNode('transform', n=f"{self.side}_{self.label}_upPV", p=clavCtrl)
        cmds.xform(upT, ws=True, t=cmds.xform(
            clavCtrl, q=True, ws=True, t=True
        ))
        cmds.xform(upT, ws=True, ro=cmds.xform(
            clavCtrl, q=True, ws=True, ro=True
        ))
        loT = cmds.createNode('transform', n=f"{self.side}_{self.label}_loPV", p=ikCtrl)
        cmds.xform(loT, ws=True, t=cmds.xform(
            ikCtrl, q=True, ws=True, t=True
        ))
        cmds.xform(loT, ws=True, ro=cmds.xform(
            ikCtrl, q=True, ws=True, ro=True
        ))
        pc = cmds.pointConstraint([upT, loT], pvPar, n=f"{pvPar}_pc", mo=1)

        # Connections.
        cmds.addAttr(ikCtrl, ln="IK_FK_Switch", at="float", min=0, max=1, dv=0, k=1)

        index = 0
        for jnt in baseJoints[1::]:
            bc = cmds.createNode('blendColors', n=f"{jnt}_bc")

            cmds.connectAttr(f"{ikCtrl}.IK_FK_Switch", f"{bc}.blender")
            cmds.connectAttr(f"{FKJoints[index]}.rotate", f"{bc}.color1")
            cmds.connectAttr(f"{IKJoints[index]}.rotate", f"{bc}.color2")
            cmds.connectAttr(f"{bc}.output", f"{jnt}.rotate")


            index+=1
        fkCtrlPar = cmds.listRelatives(FKControls[0], p=True)[0]
        cmds.connectAttr(f"{ikCtrl}.IK_FK_Switch", f"{fkCtrlPar}.visibility")
        rev = cmds.createNode("reverse", n=f"{self.side}_{self.label}_IKFK_rev")
        cmds.connectAttr(f"{ikCtrl}.IK_FK_Switch", f"{rev}.input.inputX")
        cmds.connectAttr(f"{rev}.output.outputX", f"{ikGrp}.visibility")
        cmds.connectAttr(f"{rev}.output.outputX", f"{pvPar}.visibility")
        for ctrl in FKControls:
            cmds.addAttr(ctrl, ln="IK_FK_Switch", proxy=f"{ikCtrl}.IK_FK_Switch", at="float", min=0, max=1, dv=0, k=1)
        cmds.addAttr(pvCtrl, ln="IK_FK_Switch", proxy=f"{ikCtrl}.IK_FK_Switch", at="float", min=0, max=1, dv=0, k=1)

        endGrp = cmds.createNode("transform", n=f"{baseJoints[3]}_grp")
        endCtrl = cmds.createNode("transform", n=f"{baseJoints[3]}_CTRL", p=endGrp)
        endJnt = cmds.createNode("joint", n=f"{baseJoints[3]}End")
        cmds.xform(endJnt, ws=True, m=cmds.xform(
            baseJoints[3], q=True, ws=True, m=True
        ))
        cmds.parent(endJnt, baseJoints[3])
        ptc = cmds.parentConstraint(baseJoints[3], endGrp, n=f"{baseJoints[3]}_End_ptc", mo=0)
        ptc = cmds.parentConstraint(endCtrl, endJnt, n=f"{endJnt}_ptc", mo=0)
        endCtrlObject = ctrlCrv.Ctrl(
            node=endCtrl,
            shape="box",
            scale=[self.ctrlScale[0]*1.15, self.ctrlScale[1]*1.15, self.ctrlScale[2]*1.15],
            offset=[self.ctrlScale[0]*1.25, 0, 0]
        )
        endCtrlObject.giveCtrlShape()

        midGrp = cmds.createNode("transform", n=f"{baseJoints[2]}_Offset_grp")
        midCtrl = cmds.createNode("transform", n=f"{baseJoints[2]}_Offset_CTRL", p=midGrp)
        midCtrlObject = ctrlCrv.Ctrl(
            node=midCtrl,
            shape="circle",
            scale=[self.ctrlScale[0]*1.5, self.ctrlScale[1]*1.5, self.ctrlScale[2]*1.5],
            offset=[0, 0, 0],
            orient=[0, 90, 0]
        )
        midCtrlObject.giveCtrlShape()
        cmds.xform(midGrp, ws=True, t=cmds.xform(
            baseJoints[2], q=True, ws=True, t=True
        ))
        cmds.xform(midGrp, ws=True, ro=cmds.xform(
            baseJoints[2], q=True, ws=True, ro=True
        ))

        upRollJoints, loRollJoints, upIK, loIK = self.buildCounterJoints(baseJoints, socketConnector, endJnt)
        pc = cmds.pointConstraint(baseJoints[2], midGrp, n=f"{midGrp}_pc", mo=0)
        oc = cmds.orientConstraint([upRollJoints[1], loRollJoints[1]], midGrp, n=f"{midGrp}_oc", mo=0)[0]
        cmds.setAttr(f"{oc}.interpType", 2)

        # Cleanup
        cmds.parent([clavGrp, ikGrp, pvPar, cmds.listRelatives(FKControls[0], p=True)[0], endGrp, midGrp], self.plugParent)

        return IKControls, FKControls, midCtrl, endCtrl, upRollJoints, loRollJoints, upIK, loIK 
