"""FK Motion Module."""

import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds


class Limb(motionBase.MotionModuleBase):
    """Limb Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, addOffset=True, clavicle=True,
                 buildOrder: int = 2000, isMuted: bool = False, parent: str = None, 
                 mirror: bool = False, selectedPlug: str = "", selectedSocket: str = "",
                 pvMultiplier: float = 1.0, numberOfJoints: int = 11, 
                 nameSet: dict = {"Root":"Root", "Start":"Start", "Mid":"Mid", "End":"End"}) -> None:
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
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["Root"],
                plug=True
            ),
            self.nameSet["Start"]: proxy.Proxy(
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["Start"],
                plug=False,
                parent=self.nameSet["Root"]
            ),
            self.nameSet["Mid"]: proxy.Proxy(
                position=[0, 10, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["Mid"],
                parent=self.nameSet["Start"]
            ),
            self.nameSet["End"]: proxy.Proxy(
                position=[0, 10, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["End"],
                parent=self.nameSet["Mid"]
            )
        }
        if not self.clavicle:
            pass

        # Module Based Variables
        self.poleVector = None

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self) -> None:
        """Run the module."""

        '''
        TODO: 
        Note
           - This limb is comprised of the following. Parts of this description that start with a -* are in progress.
             Sections beginning with -** are left as TODO:
           - Base Three Point (plus Clavicle/Hip) generated with IK, FK, duplicates.
           -** IK Roll bones are singleRotationIKSolvers. They are two, two point systems for the shoulder and wrist.
               Shoulder > Elbow joint chain, Generate IK, parent the Shoulder to a Shoulder Connecting Joint ( all 
               shoulder points are children of this joint. Should be Clavicle > Shoulder Connector > Everything else)
               Then pointConstraint the IK to the elbow / elbow Offset? Lastely orient constraint the ElbowRollIK joint
               to the Base Shoulder rotation. Do the reverse for the Wrist, except the Wrist IK Roll bone is parented to 
               the Wrist joint. 
               This will give a clean rotation gradient and provide a static lock in the aim axis rotaiton for the shoulder/
               wrist IK roll joints. 
           -*  Ribbon Controls operate in a few ways. Shoulder IK Roll and Wrist IK Roll joints will drive the base 
               Start / End ribbon controls (usually 7 in total). The Middle most Ribbon Control is driven by the elbow offset. 
               The rest are driven by the following. 
               Upper Ribbon Controls: 
                ShoulderRollIK and Elbow > Orient Constraint > Ribbon Control Grp set to 2/1 or 1/2
                ShoulderRollIK and Elbow > Position Constraint > Ribbon Control Grp set to 2/1 or 1/2
                Elbow > Aim Constraint > Ribbon Control Offset
                The joint children of the actual control will skin to the ribbon. 
               The Ribbon is generated between 0 - 10 in x, has follicles ride along the surface that will drive the skinning
               joints.


        '''

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
        IKControls, FKControls, midCtrl, endCtrl, upRollJoints, loRollJoints, upIK, loIK = self.buildBaseControls(baseJoints, IKJoints, FKJoints, upConnector)
        self.buildRibbon(baseJoints, upRollJoints, loRollJoints, midCtrl, endCtrl)

        # Cleanup
        cmds.parent(baseJoints[0], self.moduleUtilities)

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

        # jointTools.aim([baseJoints[0]], [baseJoints[1]])
        jointTools.aimSequence([baseJoints[1], baseJoints[2], baseJoints[3]], upObj=self.poleVector)
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
    

    def buildCounterJoints(self, baseJoints, socketConnector, endJoint):
        upRollStart = cmds.createNode("joint", n=f"{baseJoints[1]}_Roll")
        upRollEnd = cmds.createNode("joint", n=f"{baseJoints[1]}_End", p=upRollStart)
        cmds.xform(upRollStart, ws=True, t=cmds.xform(
            baseJoints[1], q=True, ws=True, t=True
        ))
        cmds.xform(upRollStart, ws=True, ro=cmds.xform(
            baseJoints[1], q=True, ws=True, ro=True
        ))
        cmds.xform(upRollEnd, ws=True, t=cmds.xform(
            baseJoints[2], q=True, ws=True, t=True
        ))
        cmds.makeIdentity(upRollStart, a=True)
        cmds.parent(upRollStart, socketConnector)
        upIK = cmds.ikHandle(n=f"{upRollStart}_IK", sj=upRollStart, ee=upRollEnd,
                             sol="ikSCsolver", p=4)
        upEff = upIK[1]
        upEff = cmds.rename(upEff, upIK[0].replace("IK", "EFF"))
        upIK = upIK[0]
        pc = cmds.pointConstraint(baseJoints[2], upIK, n=f"{upIK}_pc", mo=0)
        oc = cmds.orientConstraint(baseJoints[1], upRollEnd, n=f"{upRollEnd}_oc", mo=0)
        cmds.parent(upIK, socketConnector)

        loRollStart = cmds.createNode("joint", n=f"{baseJoints[3]}_Roll")
        loRollEnd = cmds.createNode("joint", n=f"{baseJoints[3]}_End", p=loRollStart)
        cmds.xform(loRollStart, ws=True, t=cmds.xform(
            baseJoints[3], q=True, ws=True, t=True
        ))
        cmds.xform(loRollStart, ws=True, ro=cmds.xform(
            baseJoints[3], q=True, ws=True, ro=True
        ))
        cmds.xform(loRollEnd, ws=True, t=cmds.xform(
            baseJoints[2], q=True, ws=True, t=True
        ))
        cmds.makeIdentity(loRollStart, a=True)
        cmds.parent(loRollStart, baseJoints[3])
        loIK = cmds.ikHandle(n=f"{loRollStart}_IK", sj=loRollStart, ee=loRollEnd,
                             sol="ikSCsolver", p=4)
        loEff = loIK[1]
        loEff = cmds.rename(loEff, loIK[0].replace("IK", "EFF"))
        loIK = loIK[0]
        pc = cmds.pointConstraint(baseJoints[2], loIK, n=f"{loIK}_pc", mo=0)
        oc = cmds.orientConstraint(baseJoints[2], loRollEnd, n=f"{loRollEnd}_oc", mo=0)
        cmds.parent(loIK, baseJoints[3])
        
        #Cleanup
        # cmds.parent([upIK, loIK], self.moduleUtilities)

        return [upRollStart, upRollEnd], [loRollStart,loRollEnd], upIK, loIK 
         

    def buildRibbon(self, baseJoints, upRollJoints, loRollJoints, midOffset, endOffset):
        follicles = []
        follicleJoints = []
        ribbonControls = []
        ribbonGroups = []
        ribbonOffsets = []
        ribbonJoints = []

        folGrp = cmds.createNode("transform", n=f"{self.side}_{self.label}_follicles")

        tempCurve = cmds.curve(n="TempCurve_1", d=1, p=[[0,0,0], [10, 0, 0]])
        tempCurve2 = cmds.duplicate(tempCurve, n="TempCurve_2")[0]
        cmds.xform(tempCurve, ws=True, t=[0, 0.5, 0])
        cmds.xform(tempCurve2, ws=True, t=[0, -0.5, 0])

        ribbon = cmds.loft([tempCurve2, tempCurve], n=f"{self.label}_{self.label}_Bendy_rbn", ch=False)[0]
        cmds.reverseSurface(ribbon, d=3, ch=False, rpo=1)
        cmds.rebuildSurface(
            ribbon, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, 
            su=6, du=3, sv=1, dv=1, tol=0.01, fr=0, dir=2, ch=False
            )
        cmds.delete([tempCurve, tempCurve2])
        param = 0
        paramInfl = 1/(self.numberOfJoints-1)
        for i in range(self.numberOfJoints):

            #Build Follicles
            fol = cmds.createNode("transform", n=f"{self.side}_{self.label}_{i}_fol")
            folShape = cmds.createNode(
                "follicle", n=f"{self.side}_{self.label}_{i}_folShape", p=fol)
            
            cmds.connectAttr(f"{ribbon}.worldMatrix[0]", f"{folShape}.inputWorldMatrix", f=True)
            cmds.connectAttr(f"{ribbon}.local", f"{folShape}.inputSurface", f=True)
            cmds.setAttr(f"{folShape}.parameterV", 0.5)
            cmds.setAttr(f"{folShape}.parameterU", param)
            cmds.connectAttr(f"{folShape}.outRotate", f"{fol}.rotate", f=True)
            cmds.connectAttr(f"{folShape}.outTranslate", f"{fol}.translate", f=True)

            cmds.parent(fol, folGrp)

            if param > 1:
                param = 1
            param += paramInfl

            follicles.append([fol, folShape])

            # Build Joints
            jnt = cmds.createNode("joint", n=f"{self.side}_{self.label}_{i}")
            cmds.xform(jnt, ws=True, t=cmds.xform(
                fol, q=True, ws=True, t=True
            ))
            cmds.xform(jnt, ws=True, ro=cmds.xform(
                fol, q=True, ws=True, ro=True
            ))
            cmds.parent(jnt, fol)
            follicleJoints.append(jnt)

        jointTools.aimSequence(follicleJoints, upObj=self.poleVector)
        cmds.makeIdentity(follicleJoints, a=True)
        setRange = 0
        rangeDist = (1/6) * 10
        tempUpSpace = cmds.createNode('transform', n='TempUpSpace')
        cmds.xform(tempUpSpace, ws=True, t=[0, 0, -10])
        bendyCtrlGrp = cmds.createNode("transform", n=f"{self.side}_{self.label}_BendyCtrls")
        # Make Ribbon Controls
        for i in range(7):
            grp = cmds.createNode("transform", n=f"{self.side}_{self.label}_Bendy_{i}_grp", p=bendyCtrlGrp)
            offset = cmds.createNode("transform", n=f"{self.side}_{self.label}_Bendy_{i}_offset", p=grp)
            ctrl = cmds.createNode("transform", n=f"{self.side}_{self.label}_Bendy_{i}_CTRL", p=offset)
            jnt = cmds.createNode("joint", n=f"{self.side}_{self.label}_Bendy_{i}", p=ctrl)

            ribbonGroups.append(grp)
            ribbonOffsets.append(offset)
            ribbonControls.append(ctrl)
            ribbonJoints.append(jnt)

            ctrlObject = ctrlCrv.Ctrl(
                node=ctrl,
                shape="circle",
                scale=[self.ctrlScale[0]*.75, self.ctrlScale[1]*.75, self.ctrlScale[2]*.75],
                offset=[0, 0, 0],
                orient=[0, 90, 0]
            )
            ctrlObject.giveCtrlShape()

            cmds.xform(grp, ws=True, t=[setRange, 0, 0])
            setRange+=rangeDist
        jointTools.aimSequence(ribbonGroups, upObj=tempUpSpace)
        cmds.delete(tempUpSpace)

        # Bind Ribbon
        ribbonSCLS = cmds.skinCluster(ribbonJoints,
                                      ribbon,
                                      n=f"{ribbon}_scls",
                                      tsb=True,
                                      mi=1)[0]

        # Order The Controls
        ptc = cmds.parentConstraint(upRollJoints[0], ribbonGroups[0], n=f"{ribbonGroups[0]}_ptc", mo=0)
        pc = cmds.pointConstraint([upRollJoints[0], midOffset], ribbonGroups[1], n=f"{ribbonGroups[1]}_pc", mo=0)[0]
        oc = cmds.orientConstraint([upRollJoints[0], upRollJoints[1]], ribbonGroups[1], n=f"{ribbonGroups[1]}_oc", mo=0)[0]
        cmds.setAttr(f"{pc}.{upRollJoints[0]}W0", 2)
        cmds.setAttr(f"{oc}.interpType", 2)
        cmds.setAttr(f"{oc}.{upRollJoints[0]}W0", 2)
        pc = cmds.pointConstraint([upRollJoints[0], midOffset], ribbonGroups[2], n=f"{ribbonGroups[2]}_pc", mo=0)[0]
        oc = cmds.orientConstraint([upRollJoints[0],upRollJoints[1]], ribbonGroups[2], n=f"{ribbonGroups[2]}_oc", mo=0)[0]
        cmds.setAttr(f"{pc}.{midOffset}W1", 2)
        cmds.setAttr(f"{oc}.interpType", 2)
        cmds.setAttr(f"{oc}.{upRollJoints[1]}W1", 2)
        
        ptc = cmds.parentConstraint(endOffset, ribbonGroups[6], n=f"{ribbonGroups[6]}_ptc", mo=0)
        pc = cmds.pointConstraint([endOffset, midOffset], ribbonGroups[4], n=f"{ribbonGroups[4]}_pc", mo=0)[0]
        oc = cmds.orientConstraint([endOffset,loRollJoints[1]], ribbonGroups[4], n=f"{ribbonGroups[4]}_oc", mo=0)[0]
        cmds.setAttr(f"{pc}.{midOffset}W1", 2)
        cmds.setAttr(f"{oc}.interpType", 2)
        cmds.setAttr(f"{oc}.{loRollJoints[1]}W1", 2)
        pc = cmds.pointConstraint([endOffset, midOffset], ribbonGroups[5], n=f"{ribbonGroups[5]}_pc", mo=0)[0]
        oc = cmds.orientConstraint([endOffset, loRollJoints[1]], ribbonGroups[5], n=f"{ribbonGroups[5]}_oc", mo=0)[0]
        cmds.setAttr(f"{pc}.{endOffset}W0", 2)
        cmds.setAttr(f"{oc}.interpType", 2)
        cmds.setAttr(f"{oc}.{endOffset}W0", 2)
        

        ptc = cmds.parentConstraint(midOffset, ribbonGroups[3], n=f"{ribbonGroups[3]}_ptc", mo=0)

        ac = cmds.aimConstraint(midOffset, ribbonOffsets[1], n=f"{ribbonOffsets[1]}_ac",
                                aim=[1, 0, 0], u=[0, 1, 0], wut="objectRotation",
                                wuo=midOffset, wu=[0, 1, 0], sk="x", mo=0)
        ac = cmds.aimConstraint(midOffset, ribbonOffsets[2], n=f"{ribbonOffsets[2]}_ac",
                                aim=[1, 0, 0], u=[0, 1, 0], wut="objectRotation",
                                wuo=midOffset, wu=[0, 1, 0], sk="x", mo=0)
        ac = cmds.aimConstraint(midOffset, ribbonOffsets[5], n=f"{ribbonOffsets[5]}_ac",
                                aim=[-1, 0, 0], u=[0, 1, 0], wut="objectRotation",
                                wuo=midOffset, wu=[0, 1, 0], sk="x", mo=0)
        ac = cmds.aimConstraint(midOffset, ribbonOffsets[4], n=f"{ribbonOffsets[4]}_ac",
                                aim=[-1, 0, 0], u=[0, 1, 0], wut="objectRotation",
                                wuo=midOffset, wu=[0, 1, 0], sk="x", mo=0)
        
        # Cleanup
        cmds.parent(ribbon, self.moduleUtilities)
        cmds.parent(folGrp, self.moduleUtilities)
        cmds.parent(bendyCtrlGrp, self.plugParent)
        
        
            
            