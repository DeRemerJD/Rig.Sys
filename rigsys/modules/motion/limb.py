"""FK Motion Module."""

import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds


class FK(motionBase.MotionModuleBase):
    """FK Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, addOffset=True, clavicle=True,
                 buildOrder: int = 2000, isMuted: bool = False, parent: str = None, 
                 mirror: bool = False, selectedPlug: str = "", selectedSocket: str = "",
                 pvMultiplier: float = 1.0, numberOfJoints: int = 11) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, parent, mirror, selectedPlug, selectedSocket)
        
        self.addOffset = addOffset
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        self.clavicle = clavicle

        # Module Specific Exposed Variables
        self.pvMultiplier = pvMultiplier
        self.numberOfJoints

        self.proxies = {
            "AltStart": proxy.Proxy(
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Clavicle",
                plug=True
            ),
            "Start": proxy.Proxy(
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Shoulder",
                plug=False
            ),
            "Mid": proxy.Proxy(
                position=[0, 10, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Elbow",
                parent="Start"
            ),
            "End": proxy.Proxy(
                position=[0, 10, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Wrist",
                parent="Mid"
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
        Chains for FK, IK, Base joints + Clavicle.
        Build a surface from 0 to 10, and across x number of spans.
        Make x number of controls for the bendy limb and n number of joints
        bind the surface to the x ctrl joints. Have a specified start mid end ctrl/joint
        bind the designated controls to the matching position on the base skel

        lo = cmds.loft(["TestCurve", "TestCurve1"], n="TESTSURFACE", ch=0)
        print(lo)
        isolateSelect -update "modelPanel4";
        ['TESTSURFACE']
        isolateSelect -addSelectedObjects modelPanel4;
        select -r TESTSURFACE ;
        reverseSurface -d 3 -ch 1 -rpo 1 "TESTSURFACE";
        // Warning: History will be off for the command since Keep Originals is off and a selected item has no history.
        isolateSelect -update "modelPanel4";
        // Result: TESTSURFACE
        isolateSelect -addSelectedObjects modelPanel4;
        rebuildSurface -ch 1 -rpo 1 -rt 0 -end 1 -kr 0 -kcp 0 -kc 0 -su 6 -du 3 -sv 1 -dv 1 -tol 0.01 -fr 0  -dir 2 "TESTSURFACE";
        // Warning: History will be off for the command since Keep Originals is off and a selected item has no history.
        isolateSelect -update "modelPanel4";
        // Result: TESTSURFACE
        isolateSelect -addSelectedObjects modelPanel4;


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

        plugPosition = self.proxies["AltStart"].position
        plugRotation = self.proxies["AltStart"].rotation
        # MAKE MODULE NODES
        self.moduleHierarchy()

        # Make Plug Transforms
        self.plugParent = self.createPlugParent(
            position=plugPosition, rotation=plugRotation
        )
        self.worldParent = self.createWorldParent()

        baseJoints, FKJoints, IKJoints, upConnector = self.buildSkeleton()
        IKControls, FKControls, midCtrl, endCtrl, upRollJoints, loRollJoints, upIK, loIK = self.buildBaseControls(baseJoints, IKJoints, FKJoints, upConnector)
        

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
            destination = jointTools.getPoleVector(baseJoints[1], baseJoints[2], baseJoints[3], self.pvMultiplier)
            cmds.xform(self.poleVector, ws=True, t=destination)
            
            for i in ["X", "Y", "Z"]:
                cmds.setAttr(f"{self.poleVector}.localScale{i}", 0, l=True)

        # jointTools.aim()
        jointTools.aimSequence([baseJoints[1], baseJoints[2], baseJoints[3]], upObj=self.poleVector)

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
            index = 1
            if jnt != baseJoints[1]:
                cmds.parent(fkJnt, f"{baseJoints[index]}_FK")
                cmds.parent(ikJnt, f"{baseJoints[index]}_IK")
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
        ikGrp = cmds.createNode('transform', n=f"{IKJoints[2]}_IK_grp")
        ikCtrl = cmds.createNode('transform', n=f"{IKJoints[2]}_IK_CTRL", p=ikGrp)
        cmds.xform(ikGrp, ws=True, t=cmds.xform(
            IKJoints[2], q=True, ws=True, t=True
        ))
        ikCtrlObject = ctrlCrv.Ctrl(
            node=ikCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
            offset=[0, 0, 0]
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
        oc = cmds.orientConstraint(ikCtrl, IKJoints[2])

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
                offset=[0, 0, 0]
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
            n=clavCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0]*1.5, self.ctrlScale[1]*1.5, self.ctrlScale[2]*1.5],
            offset=[0, 0, 0]
        )
        clavCtrlObject.giveCtrlShape()
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

            cmds.connectAttr(f"{ikCtrl}.IK_FK_Switch", f"{bc}.blend")
            cmds.connectAttr(f"{FKJoints[index]}.rotate", f"{bc}.color1")
            cmds.connectAttr(f"{FKJoints[index]}.rotate", f"{bc}.color2")
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
        endJnt = cmds.createNode("joint", n=f"{baseJoints[3]}_End")
        cmds.xform(endJnt, ws=True, m=cmds.xform(
            baseJoints[3], ws=True, m=True
        ))
        ptc = cmds.parentConstraint(baseJoints[3], endGrp, n=f"{baseJoints[3]}_End_ptc", mo=0)
        ptc = cmds.parentConstraint(endCtrl, endJnt, n=f"{endJnt}_ptc", mo=0)
        endCtrlObject = ctrlCrv.Ctrl(
            node=endCtrl,
            shape="box",
            scale=[self.ctrlScale[0]*1.15, self.ctrlScale[1]*1.15, self.ctrlScale[2]*1.15],
            offset=[self.ctrlScale*1.25, 0, 0]
        )
        endCtrlObject.giveCtrlShape()

        midGrp = cmds.createNode("transform", n=f"{baseJoints[2]}_Offset_grp")
        midCtrl = cmds.createNode("transform", n=f"{baseJoints[2]}_Offset_CTRL", p=midGrp)
        midCtrlObject = ctrlCrv.Ctrl(
            node=midCtrl,
            shape="circle",
            scale=[self.ctrlScale[0]*1.5, self.ctrlScale[1]*1.5, self.ctrlScale[2]*1.5],
            offset=[0, 0, 0]
        )
        midCtrlObject.giveCtrlShape()

        upRollJoints, loRollJoints, upIK, loIK = self.buildCounterJoints(baseJoints, socketConnector, endJnt)
        pc = cmds.pointConstraint(midGrp, baseJoints[2], n=f"{midGrp}_pc", mo=0)
        oc = cmds.orientConstraint([upRollJoints[1], loRollJoints[1]], midGrp, n=f"{midGrp}_oc", mo=0)

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
        cmds.parent(loRollStart, endJoint)
        upIK = cmds.ikHandle(n=f"{loRollStart}_IK", sj=loRollStart, ee=loRollEnd,
                             sol="ikSCsolver", p=4)
        loEff = loIK[1]
        loEff = cmds.rename(loEff, loIK[0].replace("IK", "EFF"))
        loIK = loIK[0]
        pc = cmds.pointConstraint(baseJoints[2], loIK, n=f"{loIK}_pc", mo=0)
        oc = cmds.orientConstraint(endJoint, loRollEnd, n=f"{loRollEnd}_oc", mo=0)

        return [upRollStart, upRollEnd], [loRollStart,loRollEnd], upIK, loIK

        

        

    def buildRibbon(self, baseJoints, upCounterJoints, loCounterJoints):
        follicles = []
        follicleJoints = []
        ribbonControls = []
        ribbonGroups = []
        ribbonOffset = []
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
        param = 0
        paramInfl = 1/(self.numberOfJoints-1)
        for i in range(self.numberOfJoints):

            #Build Follicles
            fol = cmds.createNode("transform", n=f"{self.side}_{self.label}_{i}_fol")
            folShape = cmds.createNode(
                "follicle", n=f"{self.side}_{self.label}_{i}_folShape", p=fol)
            
            cmds.connectAttr(f"{ribbon}.worldMatrix[0]", f"{folShape}.inputWorldMatrix", f=True)
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
        
        # Make Ribbon Controls
        for i in range(7):
            grp = cmds.createNode("transform", n=f"{self.side}_{self.label}_Bendy_{i}_grp")
            offset = cmds.createNode("transform", n=f"{self.side}_{self.label}_Bendy_{i}_offset", p=grp)
            ctrl = cmds.createNode("transform", n=f"{self.side}_{self.label}_Bendy_{i}_CTRL", p=offset)
            jnt = cmds.createNode("joint", n=f"{self.side}_{self.label}_Bendy_{i}", p=ctrl)
            
            