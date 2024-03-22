"""FK / Reverse FK Motion Module."""


import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds


class FKSegment(motionBase.MotionModuleBase):
    """Root Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, addOffset=True, segments=5,
                 reverse=True, IKRail=True, buildOrder: int = 2000, isMuted: bool = False, parent: str = None,
                 mirror: bool = False, selectedPlug: str = "", selectedSocket: str = "") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, parent, mirror, selectedPlug, selectedSocket)

        if ctrlScale is None:
            ctrlScale = [1.0, 1.0, 1.0]

        self.addOffset = addOffset
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        self.segments = segments
        self.reverse = reverse
        self.IKRail = IKRail

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
        }
        self.plugs = {
            "Local": None,
            "World": None
        }
        # if self.segments > 1:
        #     for i in range(1, self.segments):
        #         self.sockets[str(i)] = None

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
        self.plugs["Local"] = self.plugParent
        self.plugs["World"] = self.worldParent

        # CREATING NODES
        FKCtrls = []
        FKGrps = []
        OffsetCtrls = []
        OffsetGrps = []
        RFKCtrls = []
        RFKGrps = []
        RFKOffsets = []
        # MODULE STRUCTURE #
        for key, proxy in self.proxies.items():
            if key != "UpVector":
                fGrp = cmds.createNode("transform", n="{}_{}_grp".format(
                    self.getFullName(), self.proxies[key].name))
                fCtrl = cmds.createNode("transform", n="{}_{}_CTRL".format(
                    self.getFullName(), self.proxies[key].name))

                cmds.parent(fCtrl, fGrp)
                FKCtrls.append(fCtrl)
                FKGrps.append(fGrp)

                cmds.xform(fGrp, ws=True, t=self.proxies[key].position)

                if self.addOffset:
                    oGrp = cmds.createNode("transform", n="{}_{}Local_grp".format(
                        self.getFullName(), self.proxies[key].name))
                    oCtrl = cmds.createNode("transform", n="{}_{}Local_CTRL".format(
                        self.getFullName(), self.proxies[key].name))

                cmds.parent(oCtrl, oGrp)
                OffsetCtrls.append(oCtrl)
                OffsetGrps.append(oGrp)
                cmds.xform(oGrp, ws=True, t=self.proxies[key].position)

                if self.reverse:
                    rGrp = cmds.createNode("transform", n="{}_{}_Rev_grp".format(
                        self.getFullName(), self.proxies[key].name))
                    rCtrl = cmds.createNode("transform", n="{}_{}_Rev_CTRL".format(
                        self.getFullName(), self.proxies[key].name))
                    rOff = cmds.createNode("transform", n="{}_{}_Rev_offset".format(
                        self.getFullName(), self.proxies[key].name))

                    cmds.parent(rCtrl, rGrp)
                    cmds.parent(rOff, rCtrl)

                    RFKCtrls.append(rCtrl)
                    RFKGrps.append(rGrp)
                    RFKOffsets.append(rOff)
                    cmds.xform(rGrp, ws=True, t=self.proxies[key].position)

        # Orient FK
        jointTools.aimSequence(
            targets=FKGrps, aimAxis="+x", upAxis="-z",
            upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy")
        jointTools.aimSequence(
            targets=FKCtrls, aimAxis="+x", upAxis="-z",
            upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy")
        if self.reverse:
            jointTools.aimSequence(
                targets=RFKGrps, aimAxis="+x", upAxis="-z",
                upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy")
            jointTools.aimSequence(
                targets=RFKOffsets, aimAxis="+x", upAxis="-z",
                upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy")
            jointTools.aimSequence(
                targets=RFKCtrls, aimAxis="+x", upAxis="-z",
                upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy")
            for rOff in RFKOffsets:
                cmds.setAttr(f"{rOff}.rotateOrder", 5)
        if self.addOffset:
            jointTools.aimSequence(
                targets=OffsetGrps, aimAxis="+x", upAxis="-z",
                upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy")
            jointTools.aimSequence(
                targets=OffsetCtrls, aimAxis="+x", upAxis="-z",
                upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy")

        # Parenting
        index = 1
        for fCtrl in FKCtrls:
            if not index >= len(FKCtrls):
                cmds.parent(FKGrps[index], fCtrl)
            index += 1
            fkCtrlObject = ctrlCrv.Ctrl(
                node=fCtrl,
                shape="sphere",
                scale=[self.ctrlScale[0] * .75, self.ctrlScale[1] * .75, self.ctrlScale[2] * .75],
                offset=[0, 0, -10]
            )
            fkCtrlObject.giveCtrlShape()

        if self.reverse:
            RFKGrps.reverse()
            RFKCtrls.reverse()
            RFKOffsets.reverse()
            index = 1
            for rOff in RFKOffsets:
                if not index >= len(RFKOffsets):
                    cmds.parent(RFKGrps[index], rOff)

                md = cmds.createNode("multiplyDivide", n=f"{rOff}_md")
                for i in ["X", "Y", "Z"]:
                    cmds.setAttr(f"{md}.input2{i}", -1)
                cmds.connectAttr(f"{FKCtrls[index*-1]}.rotate", f"{md}.input1")
                cmds.connectAttr(f"{md}.output", f"{rOff}.rotate")
                index += 1

            # Make Controls
            for rCtrl in RFKCtrls:
                reverseCtrlObject = ctrlCrv.Ctrl(
                    node=rCtrl,
                    shape="box",
                    scale=[self.ctrlScale[0] * .5, self.ctrlScale[1] * .5, self.ctrlScale[2] * .5],
                    offset=[0, 0, -10]
                )
                reverseCtrlObject.giveCtrlShape()
            cmds.parent(RFKGrps[0], FKCtrls[-1])

        if self.addOffset:
            if self.reverse:
                RFKCtrls.reverse()
                for rCtrl, oGrp in zip(RFKCtrls, OffsetGrps):
                    ptc = cmds.parentConstraint(rCtrl, oGrp, n=oGrp + "_ptc", mo=0)[0]
                    cmds.setAttr(ptc + ".interpType", 2)
                RFKCtrls.reverse()
            else:
                for fCtrl, oGrp in zip(FKCtrls, OffsetGrps):
                    ptc = cmds.parentConstraint(rCtrl, oGrp, n=oGrp + "_ptc", mo=0)[0]
                    cmds.setAttr(ptc + ".interpType", 2)

            # Add Controls
            for oCtrl in OffsetCtrls:
                offsetCtrlObject = ctrlCrv.Ctrl(
                    node=oCtrl,
                    shape="circle",
                    orient=[0, 90, 0],
                    scale=self.ctrlScale
                )
                offsetCtrlObject.giveCtrlShape()

        FKJoints = []
        coords = []

        if self.IKRail:
            IKJoints = []
            # Create Guide joints
            for fCtrl in FKCtrls:
                fkJnt = cmds.createNode("joint", n=fCtrl.replace("_CTRL", "_guide"))
                ikJnt = cmds.createNode("joint", n=fCtrl.replace("_CTRL", "_ik"))
                cmds.xform(fkJnt, ws=True, t=cmds.xform(fCtrl, q=True, ws=True, t=True))
                cmds.xform(fkJnt, ws=True, ro=cmds.xform(fCtrl, q=True, ws=True, ro=True))
                cmds.makeIdentity(fkJnt, a=True)
                FKJoints.append(fkJnt)

                cmds.xform(ikJnt, ws=True, t=cmds.xform(fCtrl, q=True, ws=True, t=True))
                cmds.xform(ikJnt, ws=True, ro=cmds.xform(fCtrl, q=True, ws=True, ro=True))
                cmds.makeIdentity(ikJnt, a=True)
                IKJoints.append(ikJnt)

            index = 0
            for ikJnt in IKJoints:
                if ikJnt != IKJoints[-1]:
                    cmds.parent(IKJoints[index + 1], ikJnt)
                index += 1

            # Get coords
            for fkJnt in FKJoints:
                t = cmds.xform(fkJnt, q=True, ws=True, t=True)
                coords.append(t)
            spans = len(coords) - 1

            # Make Curves
            ikCurve = cmds.curve(
                n=f"{self.getFullName()}_IKCurve", p=coords, d=3)
            cmds.rebuildCurve(ikCurve, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=spans, d=1, ch=False)

            ikCurveShape = cmds.listRelatives(ikCurve, c=True, s=True)[0]
            ikCurveShape = cmds.rename(ikCurveShape, ikCurve + "Shape")

            ik = cmds.ikHandle(
                n=f"{self.getFullName()}_IKHandle", sj=IKJoints[0], ee=IKJoints[-1],
                sol="ikSplineSolver", c=ikCurve, ccv=False
            )

            ikHandle = ik[0]
            ikEffector = ik[1]
            ikEffector = cmds.rename(ikEffector, f"{self.getFullName()}_eff")

            tempCrv1 = cmds.duplicate(ikCurve, n=ikCurve + "TEMP_1")[0]
            tempCrv2 = cmds.duplicate(ikCurve, n=ikCurve + "TEMP_2")[0]

            cmds.xform(tempCrv1, ws=True, t=[-1, 0, 0])
            cmds.xform(tempCrv2, ws=True, t=[1, 0, 0])

            rbn = cmds.loft(tempCrv1, tempCrv2, d=3, n=f"{self.getFullName()}_rbn",
                            u=True, c=0, ar=1, ss=1, rn=0, po=0, rsn=True, ch=False)[0]
            cmds.rebuildSurface(rbn, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0, su=spans, sv=1,
                                du=3, dv=1, fr=0, dir=2, ch=False)

            rbnShape = cmds.listRelatives(rbn, c=True, s=True)[0]
            rbnShape = cmds.rename(rbnShape, rbn + "Shape")

            cmds.delete([tempCrv1, tempCrv2])

            # Make Follicles and Connections
            follicles = []
            follicleShapes = []
            follicleGrp = cmds.createNode("transform", n=f"{self.getFullName()}_follicles_grp")
            name = 0
            for fkJnt in FKJoints:
                folPar = cmds.createNode("transform", n=f"{self.getFullName()}_{name}_fol")
                fol = cmds.createNode("follicle", n=f"{self.getFullName()}_{name}_folShape", p=folPar)
                follicles.append(folPar)
                follicleShapes.append(fol)
                cmds.parent(folPar, follicleGrp)

                cmds.connectAttr(f"{rbnShape}.local", f"{fol}.inputSurface")
                cmds.connectAttr(f"{rbnShape}.worldMatrix[0]", f"{fol}.inputWorldMatrix")
                cmds.connectAttr(f"{fol}.outTranslate", f"{folPar}.translate")
                cmds.connectAttr(f"{fol}.outRotate", f"{folPar}.rotate")

                cpos = cmds.createNode("closestPointOnSurface", n=f"{self.getFullName()}_{name}_cpos")
                dm = cmds.createNode("decomposeMatrix", n=f"{self.getFullName()}_{name}_dm")

                cmds.connectAttr(f"{IKJoints[name]}.worldMatrix[0]", f"{dm}.inputMatrix")
                cmds.connectAttr(f"{dm}.outputTranslate", f"{cpos}.inPosition")
                cmds.connectAttr(f"{rbnShape}.worldSpace", f"{cpos}.inputSurface")
                cmds.connectAttr(f"{cpos}.result.parameterU", f"{fol}.parameterU")

                cmds.setAttr(f"{fol}.parameterV", .5)

                name += 1

            curveSCLS = cmds.skinCluster(
                FKJoints, ikCurve, sm=0, wd=0, mi=4, n=f"{ikCurve}_scls"
            )
            ribbonSCLS = cmds.skinCluster(
                FKJoints, rbn, sm=0, wd=0, mi=4, n=f"{rbn}_scls"
            )

            railJoints = []
            railOffsets = []
            # Make Rail Joints
            for fol, ikJnt in zip(follicles, IKJoints):
                rJntOffset = cmds.createNode("transform", n=fol.replace("_fol", "railOffset"))
                rJnt = cmds.createNode("joint", n=fol.replace("_fol", "_rail"))
                cmds.parent(rJnt, rJntOffset)
                cmds.xform(rJntOffset, ws=True, t=cmds.xform(
                    ikJnt, q=True, ws=True, t=True
                ))
                cmds.xform(rJntOffset, ws=True, ro=cmds.xform(
                    ikJnt, q=True, ws=True, ro=True
                ))
                ptc = cmds.parentConstraint(fol, rJntOffset, n=f"{rJnt}_ptc", mo=0)[0]
                cmds.setAttr(f"{ptc}.interpType", 2)

                railJoints.append(rJnt)
                railOffsets.append(rJntOffset)

            # Add Stretching
            cmds.addAttr(FKCtrls[0], ln="stretch", dv=0, min=0, max=1, at="float", k=True)
            for fCtrl in FKCtrls:
                if fCtrl != FKCtrls[0]:
                    cmds.addAttr(fCtrl, ln="stretch", proxy=f"{FKCtrls[0]}.stretch", at="float", min=0, max=1, k=True)
            if self.reverse:
                for rCtrl in RFKCtrls:
                    cmds.addAttr(rCtrl, ln="stretch", proxy=f"{FKCtrls[0]}.stretch", at="float", min=0, max=1, k=True)
            if self.addOffset:
                for oCtrl in OffsetCtrls:
                    cmds.addAttr(oCtrl, ln="stretch", proxy=f"{FKCtrls[0]}.stretch", at="float", min=0, max=1, k=True)

            ci = cmds.createNode("curveInfo", n=f"{self.getFullName()}_ci")
            stretchMD = cmds.createNode("multiplyDivide", n=f"{self.getFullName()}_md")
            stretchBC = cmds.createNode("blendColors", n=f"{self.getFullName()}_md")
            cmds.connectAttr(f"{ikCurveShape}.worldSpace", f"{ci}.inputCurve")
            cmds.connectAttr(f"{ci}.arcLength", f"{stretchMD}.input1.input1X")
            cmds.setAttr(f"{stretchMD}.operation", 2)
            ciLen = cmds.getAttr(f"{ci}.arcLength")
            cmds.setAttr(f"{stretchMD}.input2.input2X", ciLen)
            cmds.setAttr(f"{stretchBC}.color2.color2R", 1.0)
            cmds.connectAttr(f"{stretchMD}.output.outputX", f"{stretchBC}.color1.color1R")
            cmds.connectAttr(f"{FKCtrls[0]}.stretch", f"{stretchBC}.blender")
            for ikJnt in IKJoints:
                if ikJnt != IKJoints[-1]:
                    cmds.connectAttr(f"{stretchBC}.output.outputR", f"{ikJnt}.scaleX")

            # If Offsets add vis Toggle
            if self.addOffset:
                cmds.addAttr(FKCtrls[0], ln="localVisibility", dv=0, min=0, max=1, at="float", k=True)
                for fCtrl in FKCtrls:
                    if fCtrl != FKCtrls[0]:
                        cmds.addAttr(fCtrl, ln="localVisibility", proxy=f"{FKCtrls[0]}.localVisibility", at="float",
                                     min=0, max=1, k=True)
                if self.reverse:
                    for rCtrl in RFKCtrls:
                        cmds.addAttr(rCtrl, ln="localVisibility", proxy=f"{FKCtrls[0]}.localVisibility", at="float",
                                     min=0, max=1, k=True)

                for oGrp in OffsetGrps:
                    cmds.connectAttr(f"{FKCtrls[0]}.localVisibility", f"{oGrp}.visibility")

            # Parenting
            cmds.parent([ikHandle, ikCurve, rbn, follicleGrp], self.moduleUtilities)
            cmds.parent(FKGrps[0], self.plugParent)
            if self.addOffset:
                cmds.parent(OffsetGrps, self.plugParent)
            cmds.parent(railOffsets, self.plugParent)
            cmds.parent(FKJoints, self.plugParent)
            cmds.parent(IKJoints[0], self.plugParent)

        if self.reverse:
            if self.addOffset:
                for oCtrl, fkJnt in zip(OffsetCtrls, FKJoints):
                    ptc = cmds.parentConstraint(oCtrl, fkJnt, n=f"{fkJnt}_ptc", mo=0)[0]
                    cmds.setAttr(f"{ptc}.interpType", 2)
            else:
                for rCtrl, fkJnt in zip(RFKCtrls, FKJoints):
                    ptc = cmds.parentConstraint(rCtrl, fkJnt, n=f"{fkJnt}_ptc", mo=0)[0]
                    cmds.setAttr(f"{ptc}.interpType", 2)
        else:
            for fkCtrl, fkJnt in zip(FKCtrls, FKJoints):
                ptc = cmds.parentConstraint(fkCtrl, fkJnt, n=f"{fkJnt}_ptc", mo=0)[0]
                cmds.setAttr(f"{ptc}.interpType", 2)

        index = 0
        for i in railJoints:
            self.sockets[f"Rail_{index}"] = i
            index += 1

        self.addSocketMetaData()
        # TODO:
        '''
        Hierarchy of Rig / Components
        N number items
            - FK Skel: Floating Joints.
            - FK Ctrls: Typical Parent - Child relationship .
              (ParCtrlGrp > ParCtlr > ChildCtrlGrp > ChildCtrl).
            - RFK Skel: Hijack the FK Skel; Floating number of N items.
            - RFK Ctrls: Reverse parent child order of FK; add an offset grp / transform
              to be a child of the Ctrl and reverse its rotation order, and rotation input
              from the matching FK control.
            - Offset Skel: Hijack the FK floating joints.
            - Offset Ctrls:Single point Ctrls that match the FK or RFK xforms.
              ( If FK, match FK, if RFK match RFK) These ctrls should be free floating,
              constrained to the relevant node.
            - IK Skel: New joints in Fk predicted order and position. If this is build FK skel becomes guides
              to deform the IK Curve and Ribbon.
            - IK Curve: Generate Curve from the skel ws coords.
            - IK Spline: Use IK Skel start / end and the IK Curve to generate.
            - Ribbon: Generate from lofting the IK Curve with an offset in a single axis.
              Do note that the ribbon should be linear in V and cubic in U
            - Follicles: Create Follicles on the ribbon, one for each IK Skel node. Use a
              'closestPointOnSurface'(CPOS) node to derive U Param value from the IK Skel joints.
              IK Skel.worldSpace > decomposeMatrix > outTranslate > CPOS.inPosition > Follicle.uParam
            - Scaling: Curve Info Node to get IK Curve length. Multiply Divide to normalize, output of
              this node should goto the primary axis scale of each (except last) IK Joint. Add Blending
              from an attribute and a blendColors node.
            - Rail Skel: New Array of floating joints, set to follow the position and rotation of the
              follicle nodes. They may require and offset node (transform for targeted rotation offsets)
              to be as clean as possible.
            - Driving the Ribbon and IK Curve:
              This can be done by either using the FK skel / guides to skin the  IK Curve and Ribbon, or
              by plugging directly into the CV / control point of the IK Curve and Ribbon. The Ribbon will
              require offsets to account for a dimension.

        '''
