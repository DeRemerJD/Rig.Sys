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

        baseJoints, FKJoints, IKJoints = self.buildSkeleton()
        

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
    
    def buildBaseControls(self, baseJoints, IKJoints, FKJoints):
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
            
            if len(FKControls) != 0:
                cmds.parent(grp, FKControls[-1])
            FKControls.append(ctrl)



    def buildCounterJoints(self, baseJoints, socketConnector, midOffset):
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
        cmds.parent(upRollStart, socketConnector)
        upIK = cmds.ikHandle(n=f"{upRollStart}_IK", sj=upRollStart, ee=upRollEnd,
                             sol="ikSCsolver", p=4)
        upEff = upIK[1]
        upEff = cmds.rename(upEff, upIK[0].replace("IK", "EFF"))
        upIK = upIK[0]

        pc = cmds.pointConstraint(midOffset, upIK, n=f"{upRollStart}_pc")[0]

        

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
            
            