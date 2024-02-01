"""FK Motion Module."""

import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds


class Hand(motionBase.MotionModuleBase):
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
            upVec = f"Finger{i}_UpVector"
            self.proxies[upVec] = proxy.Proxy(
                    position=[0, 0, 0],
                    rotation=[0, 0, 0],
                    side=self.side,
                    label=self.label,
                    name=upVec,
                    parent="Root"
                )
            for j in range(self.numOfFingerJoints):
                name = f"Finger{i}_{j}"
                if j == 0:
                    par = "Root"
                    newPar = name
                else:
                    par = f"Finger{i}_{j-1}"   
                self.proxies[name] = proxy.Proxy(
                    position=[0, 0, 0],
                    rotation=[0, 0, 0],
                    side=self.side,
                    label=self.label,
                    name=name,
                    parent=par
                )
                self.proxies[upVec].parent = "Root"

        if self.thumb:
            upVec = f"Thumb_UpVector"
            self.proxies[upVec] = proxy.Proxy(
                    position=[0, 0, 0],
                    rotation=[0, 0, 0],
                    side=self.side,
                    label=self.label,
                    name=upVec,
                    parent="Root"
                )
            for i in range(self.numOfThumbJoints):
                name = f"Thumb_{i}"
                if i == 0:
                    par = "Root"
                    newPar = name
                else:
                    par = f"Thumb_{i-1}"   
                self.proxies[name] = proxy.Proxy(
                    position=[0, 0, 0],
                    rotation=[0, 0, 0],
                    side=self.side,
                    label=self.label,
                    name=name,
                    parent=par
                )
                self.proxies[upVec].parent = "Root"


        self.socket = {
            "Start": None,
            "End": None
        }

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

        parentDict = {}
        fingerDict = {}
        Joints = []
        # Make joints
        for key, val in self.proxies.items():
            if key not in excluded:
                name = f"{self.side}_{self.label}_{val.name}"
                par = f"{self.side}_{self.label}_{val.parent}"
                jnt = cmds.createNode("joint", n=f"{name}")
                if val.parent is not None:
                    parentDict[name] = par
        
                cmds.xform(jnt, ws=True, t=val.position)
                Joints.append(jnt)
        
        for key, val in parentDict.items():
            cmds.parent(key, val)

        targets = []
        for i in range(self.numOfFingers):
            name = f"Finger{i}"
            upVectorTarget = f"{self.side}_{self.label}_{name}_UpVector_proxy"
            for jnt in Joints:
                if name in jnt:
                    targets.append(jnt)
            jointTools.aimSequence(targets=targets, upObj=upVectorTarget)
            cmds.makeIdentity(targets, a=True)
            fingerDict[name] = targets
            targets = []
        
        if self.thumb:
            targets = []
            upVectorTarget = f"{self.side}_{self.label}_Thumb_UpVector_proxy"
            for jnt in Joints:
                if "Thumb" in jnt:
                    targets.append(jnt)
            jointTools.aimSequence(targets=targets, upObj=upVectorTarget)
            cmds.makeIdentity(targets, a=True)
            fingerDict["Thumb"] = targets
            targets = []
        
        for jnt in Joints:
            if self.proxies["Root"].name in jnt:
                ac = cmds.aimConstraint(jnt, 
                                        f"{self.side}_{self.label}_{self.proxies['End'].name}_proxy",
                                        n=f"{jnt}_ac", aim=[1, 0, 0], u=[0, 1, 0], wut="vector",
                                        wu=[0, 1, 0])[0]
                cmds.delete(ac)
                cmds.makeIdentity(jnt, a=True)
                root = jnt

        globalGrp = cmds.createNode("transform", 
                                    n=f"{self.side}_{self.label}_{self.proxies['Global'].name}_grp")
        globalCtrl = cmds.createNode("transform", 
                                    n=f"{self.side}_{self.label}_{self.proxies['Global'].name}_CTRL", p=globalGrp)
        cmds.xform(globalGrp, ws=True, t=cmds.xform(
            f"{self.side}_{self.label}_{self.proxies['Global'].name}_proxy", q=True, ws=True, t=True
        ))
        cmds.xform(globalGrp, ws=True, ro=cmds.xform(
            root, q=True, ws=True, ro=True
        ))

        globalCtrlObject = ctrlCrv.Ctrl(
            node=globalCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
            offset=[0, 0, 0],
            orient=[0, 0, 0]
        )
        globalCtrlObject.giveCtrlShape()
        
        count = 0
        rate = 0
        ratio = 1 / (len(fingerDict.keys()) * .5)
        for key, val in fingerDict.items():
            # We Know the order of fingers, and finger joints.
            #
            
            md = cmds.createNode("multiplyDivide", n=f"{key}_md")
            
            fingerGrp = []
            upDnList = []
            twistList = []
            splayList = []
            nSplayList = []
            fingerCtrls = []
            val.sort()
            for jnt in val:
                grp =  cmds.createNode("transform", n=f"{jnt}_grp")
                upDn = cmds.createNode("transform", n=f"{jnt}_upDn", p=grp)
                upDnList.append(upDn)
                if jnt == val[0]:
                    twist = cmds.createNode("transform", n=f"{jnt}_twist", p=upDn)
                    splay = cmds.createNode("transform", n=f"{jnt}_splay", p=twist)
                    ctrl =  cmds.createNode("transform", n=f"{jnt}_CTRL", p=splay)
                    twistList.append(twist)
                    splayList.append(splay)
                
                elif jnt == val[1]:
                    if self.meta:
                        nSplay = cmds.createNode("transform", n=f"{jnt}_splay", p=upDn)
                        ctrl =  cmds.createNode("transform", n=f"{jnt}_CTRL", p=nSplay)
                        nSplayList.append(nSplay)
                else:
                    ctrl = cmds.createNode("transform", n=f"{jnt}_CTRL", p=upDn)
                fingerGrp.append(grp)
                fingerCtrls.append(ctrl)

                cmds.xform(grp, ws=True, m=cmds.xform(
                    jnt, q=True, ws=True, m=True
                ))
                ptc = cmds.parentConstraint(ctrl, jnt, n=f"{jnt}_ptc", mo=0)[0]

                ctrl = ctrlCrv.Ctrl(
                    node=ctrl,
                    shape="circle",
                    scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
                    offset=[0, 0, 0],
                    orient=[0, 0, 90]
                )
                ctrl.giveCtrlShape()
            for grp in fingerGrp:
                if grp != fingerGrp[0]:
                    index = fingerGrp.index(grp)
                    cmds.parent(grp, fingerCtrls[index - 1])
                else:
                    cmds.parent(grp, self.plugParent)

                # Connect Attrs and MD
            
            cmds.setAttr(f"{md}.input2.input2X", 1+rate)
            cmds.setAttr(f"{md}.input2.input2Y", 1+rate)
            cmds.setAttr(f"{md}.input2.input2Z", (1+rate)*.1)
            cmds.connectAttr(f"{globalCtrl}.rotateX", f"{md}.input1.input1X")
            cmds.connectAttr(f"{globalCtrl}.rotateY", f"{md}.input1.input1Y")
            cmds.connectAttr(f"{globalCtrl}.translateX", f"{md}.input1.input1Z")
            for upDn in upDnList:
                cmds.connectAttr(f"{globalCtrl}.rotateZ", f"{upDn}.rotateY")
            for twist in twistList:          
                cmds.connectAttr(f"{md}.output.outputX", f"{twist}.rotateY")
            for splay in splayList:
                cmds.connectAttr(f"{md}.output.outputZ", f"{splay}.rotateZ")
            for nSplay in nSplayList:
                cmds.connectAttr(f"{md}.output.outputZ", f"{nSplay}.rotateZ")
            rate-=ratio     

            count+=1  



                

        # ALL BELOW IS REFERENCE
        # index = 0
        # for fJnt in FKJoints:
        #     if fJnt != FKJoints[-1]:
        #         cmds.parent(FKJoints[index + 1], fJnt)
        #     index += 1

        # jointTools.aimSequence(
        #     FKJoints, aimAxis="+x", upAxis="-z",
        #     upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy")
        
        # FKGrps = []
        # FKCtrls = []
        # for fJnt in FKJoints:
        #     grp = cmds.createNode("transform", n=f"{fJnt}_grp")
        #     ctrl = cmds.createNode("transform", n=f"{fJnt}_CTRL")
        #     cmds.parent(ctrl, grp)

        #     cmds.xform(grp, ws=True, t=cmds.xform(
        #         fJnt, q=True, ws=True, t=True
        #     ))
        #     cmds.xform(grp, ws=True, ro=cmds.xform(
        #         fJnt, q=True, ws=True, ro=True
        #     ))

        #     FKGrps.append(grp)
        #     FKCtrls.append(ctrl)

        #     if self.addOffset:
        #         oGrp = cmds.createNode("transform", n=f"{fJnt}_grp")
        #         oCtrl = cmds.createNode("transform", n=f"{fJnt}_CTRL")
        #         cmds.parent(oCtrl, oGrp)

        #         cmds.xform(grp, ws=True, t=cmds.xform(
        #             fJnt, q=True, ws=True, t=True
        #         ))
        #         cmds.xform(grp, ws=True, ro=cmds.xform(
        #             fJnt, q=True, ws=True, ro=True
        #         ))

        #         cmds.parent(oGrp, ctrl)

        #         ptc = cmds.parentConstraint(ctrl, fJnt, n=f"{fJnt}_ptc", mo=0)[0]
        #         cmds.setAttr(f"{ptc}.interpType", 2)
        #         sc = cmds.scaleConstraint(ctrl, fJnt, n=f"{fJnt}_sc", mo=0)
        #     else:
        #         ptc = cmds.parentConstraint(ctrl, fJnt, n=f"{fJnt}_ptc", mo=0)[0]
        #         cmds.setAttr(f"{ptc}.interpType", 2)
        #         sc = cmds.scaleConstraint(ctrl, fJnt, n=f"{fJnt}_sc", mo=0)