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
        OffsetCtrls = []
        OffsetGrps = []        
        RFKCtrls = []
        RFKGrps = []
        RFKOffsets = []
        ### MODULE STRUCTURE ###
        for key, proxy in self.proxies.items():
            if key is not "UpVector" or key is not "End":
                fgrp = cmds.createNode("transform", n="{}_{}_grp".format(
                    self.getFullName(), self.proxies[key].name))
                fctrl = cmds.createNode("transform", n="{}_{}_CTRL".format(
                    self.getFullName(), self.proxies[key].name))
                
                cmds.parent(fctrl, fgrp)
                FKCtrls.append(fctrl)
                FKGrps.append(fgrp)
                
                if self.addOffset:
                    pass

                if self.reverse:
                    rgrp = cmds.createNode("transform", n="{}_{}_Rev_grp".format(
                    self.getFullName(), self.proxies[key].name))
                    rctrl = cmds.createNode("transform", n="{}_{}_Rev_CTRL".format(
                    self.getFullName(), self.proxies[key].name))
                    roff = cmds.createNode("transform", n="{}_{}_Rev_offset".format(
                    self.getFullName(), self.proxies[key].name))

                    cmds.parent(rctrl, rgrp)
                    cmds.parent(roff, rctrl)

                    RFKCtrls.append(rctrl)
                    RFKGrps.append(rgrp)
                    RFKOffsets.append(roff)


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

        cmds.delete(RFKGrps[-1])

        RFKCtrls.pop(-1)
        RFKGrps.pop(-1)
        RFKOffsets.pop(-1)

        reverseEnd = cmds.createNode("transform", n=f"{self.getFullName()}_ReverseParentTarget")
        

        # REFERENCE: DELETE ME LATER 
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
