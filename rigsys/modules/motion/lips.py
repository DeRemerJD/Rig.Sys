"""Lip Motion Module."""


import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds
import math as m


class Lips(motionBase.MotionModuleBase):
    """Root Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, numberOfJoints: int = 5, 
                 lipSegments: int = 3, jawTarget: str = None, buildOrder: int = 2000, isMuted: bool = False, parent: str = None,
                 mirror: bool = False, bypassProxiesOnly: bool = True, selectedPlug: str = "", selectedSocket: str = "",
                 aimAxis: str = "+x", upAxis: str = "-z") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, 
                         parent, mirror, bypassProxiesOnly, selectedPlug, 
                         selectedSocket, aimAxis, upAxis)
        
        '''
        The lips will have the following controls.
        1: Up Lip and Lo Lip Offset. These will control the whole up lip or lo lip array,  up to the corners.
        2: Lip Controls will move the specific lip point.
        3: Corners will move everything up to the middle lip control. 
        4: Mouth controls are a mouth, up mouth and lo mouth. 
            Mouth moves the whole lip module
            Up and Lo mouth moves the middle lip control, lo or up array through the corners for a curved offset.
            Mouth does not move up and lo mouth. Only lip controls, offsets, corners
            Lo mouth should move with jaw (optional)
            Up and lo mouth blend the parent of the Mouth to offset visual position. 
        The inner workings
        n number of lip controls will be placed along a curve that gets generated across x spans / segments. 
            the u value of each lip will be input into an ease function to determine its positional influence.
            Example: 
            import maya.cmds as cmds
            import math as m

            def easeInOutSine(input = 1):
                return -(m.cos(m.pi * input) - 1) / 2

            Do note that each transform axis will / can have a different easing method, IE: In Out Cosine,  Up Down Circle
        Lip controls aim at the next closes inner lip control.
        Corners orient to the previous inner upper / lower lip control
        Note: Lips aim to the parent of each target. This allows for localized transforms while allowing
              the methods for easing to affect the lips when moving the jaw, mouth or corner controls.

        '''

        if ctrlScale is None:
            ctrlScale = [1.0, 1.0, 1.0]

        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        self.lipSegments = lipSegments
        self.numberOfJoints = numberOfJoints
        self.jawTarget = jawTarget
        self.lipProxies = []
        self.upLipProxies = []
        self.loLipProxies = []
        

        self.proxies = {
            "Mouth": proxy.Proxy(
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side="M",
                label=self.label,
                name="Mouth",
                plug=True
            ),
            "UpMouth": proxy.Proxy(
                position=[0, 10, 0],
                rotation=[0, 0, 0],
                side="M",
                label=self.label,
                name="UpMouth",
                parent="Mouth"
            ),
            "LoMouth": proxy.Proxy(
                position=[0, 10, 0],
                rotation=[0, 0, 0],
                side="M",
                label=self.label,
                name="LoMouth",
                parent="Mouth"
            ),
            "UpVector": proxy.Proxy(
                position=[0, 0, 10],
                rotation=[0, 0, 0],
                side="M",
                label=self.label,
                name="UpVector",
                parent="Mouth"
            )
        }
        # Duplicate a full lip range or a half lip range for proxies? Probably full... how to?
        if self.lipSegments < 3:
            self.lipSegments = 3
        if self.lipSegments >= 3:
            
            par = "Mouth"
            self.proxies[f"M_Up{self.label}"] = proxy.Proxy(
                        position=[0, 0.25, 0],
                        rotation=[0, 0, 0],
                        side="M",
                        label=self.label,
                        name=f"M_Up{self.label}",
                        parent=par
                    )
            self.proxies[f"M_Lo{self.label}"] = proxy.Proxy(
                        position=[0, -0.25, 0],
                        rotation=[0, 0, 0],
                        side="M",
                        label=self.label,
                        name=f"M_Lo{self.label}",
                        parent=par
                    )
            self.lipProxies.append(f"{self.side}_{self.label}_M_Up{self.label}")
            self.lipProxies.append(f"{self.side}_{self.label}_M_Lo{self.label}")
            for i in range(0, self.lipSegments+1):
                lUpLipLabel = f"L_Up{self.label}{i}"
                rUpLipLabel = f"R_Up{self.label}{i}"
                lLoLipLabel = f"L_Lo{self.label}{i}"
                rLoLipLabel = f"R_Lo{self.label}{i}"
                lCornerLabel = f"L_Corner{self.label}"
                rCornerLabel = f"R_Corner{self.label}"
                
                if i > 0:
                    if i != self.lipSegments:
                        self.proxies[lUpLipLabel] = proxy.Proxy(
                            position=[i, 0.25, 0],
                            rotation=[0, 0, 0],
                            side="M",
                            label=self.label,
                            name=lUpLipLabel,
                            parent=f"M_Up{self.label}"
                        )
                        self.proxies[rUpLipLabel] = proxy.Proxy(
                            position=[i*-1, 0.25, 0],
                            rotation=[0, 0, 0],
                            side="M",
                            label=self.label,
                            name=rUpLipLabel,
                            parent=f"M_Up{self.label}"
                        )
                        self.proxies[lLoLipLabel] = proxy.Proxy(
                            position=[i, -0.25, 0],
                            rotation=[0, 0, 0],
                            side="M",
                            label=self.label,
                            name=lLoLipLabel,
                            parent=f"M_Lo{self.label}"
                        )
                        self.proxies[rLoLipLabel] = proxy.Proxy(
                            position=[i*-1, -0.25, 0],
                            rotation=[0, 0, 0],
                            side="M",
                            label=self.label,
                            name=rLoLipLabel,
                            parent=f"M_Lo{self.label}"
                        )
                        self.upLipProxies.append(f"{self.side}_{self.label}_{lUpLipLabel}")
                        self.upLipProxies.append(f"{self.side}_{self.label}_{rUpLipLabel}")
                        self.loLipProxies.append(f"{self.side}_{self.label}_{lLoLipLabel}")
                        self.loLipProxies.append(f"{self.side}_{self.label}_{rLoLipLabel}")
                    else:
                        self.proxies[lCornerLabel] = proxy.Proxy(
                            position=[i, 0, 0],
                            rotation=[0, 0, 0],  
                            side="M",
                            label=self.label,
                            name=lCornerLabel,
                            parent=f"M_Up{self.label}"
                        )
                        self.proxies[rCornerLabel] = proxy.Proxy(
                            position=[i*-1, 0, 0],
                            rotation=[0, 0, 0],
                            side="M",
                            label=self.label,
                            name=rCornerLabel,
                            parent=f"M_Up{self.label}"
                        )
                        self.lipProxies.append(f"{self.side}_{self.label}_{lCornerLabel}")
                        self.lipProxies.append(f"{self.side}_{self.label}_{rCornerLabel}")
        self.sockets = {
        }
        self.plugs = {
            "Local": None,
            "World": None
        }

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()

    def buildModule(self) -> None:
        """Run the module."""
        plugPosition = self.proxies["Mouth"].position
        plugRotation = self.proxies["Mouth"].rotation
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
        # Take proxies, make curve between them. Then generate joints with names based on side, counting up / down. 
        # Place joints on closest point of curve u param.

        # Lists of proxies split into up/lo, left/right
        upLipLeft = self.upLipProxies[::2]
        upLipRight = self.upLipProxies[1::2]
        loLipLeft = self.loLipProxies[::2]
        loLipRight = self.loLipProxies[1::2]

        # Lists generated for corner to corner up and lo proxies. 
        fullRangeUp = []
        fullRangeLo = []
        fullRangeUp.append(f"{self.lipProxies[2]}_proxy")
        fullRangeLo.append(f"{self.lipProxies[2]}_proxy")
        for up, lo in zip(upLipLeft, loLipLeft): 
            uProxy = f"{up}_proxy"
            lProxy = f"{lo}_proxy"
            fullRangeUp.append(uProxy)
            fullRangeLo.append(lProxy)
        fullRangeUp.append(f"{self.lipProxies[0]}_proxy")
        fullRangeLo.append(f"{self.lipProxies[1]}_proxy")
        for up, lo in zip(upLipRight[::-1], loLipRight[::-1]):
            uProxy = f"{up}_proxy"
            lProxy = f"{lo}_proxy"
            fullRangeUp.append(uProxy)
            fullRangeLo.append(lProxy)
        fullRangeUp.append(f"{self.lipProxies[3]}_proxy")
        fullRangeLo.append(f"{self.lipProxies[3]}_proxy")

        # proxy points in list corner to corner for curve generation
        upRangePoints = []
        loRangePoints = []
        for up, lo in zip(fullRangeUp, fullRangeLo): # Making points for curve gen
            upRangePoints.append(cmds.xform(up, q=True, ws=True, t=True))
            loRangePoints.append(cmds.xform(lo, q=True, ws=True, t=True))

        upCurve = cmds.curve(n="upLipCurve_TEMP", p=upRangePoints, d=3) # Make curve, rebuild so its a 0-1 param range
        cmds.rebuildCurve(upCurve, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(self.lipSegments*2), d=3, ch=False)

        loCurve = cmds.curve(n="loLipCurve_TEMP", p=loRangePoints, d=3) # Make curve, rebuild so its a 0-1 param range
        cmds.rebuildCurve(loCurve, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(self.lipSegments*2), d=3, ch=False)

        # Add to joints if even so we have a middle lip point
        if self.numberOfJoints % 2 == 0:
            self.numberOfJoints += 1

        cornerJoints = [] # For corners, 0 Left, 1 Right
        upLipJoints = [] # All up lips minus the corners
        loLipJoints = [] # All lo lips minus the corners
        # Delete Later
        cInfoNodes = []

        infl = 1 / (self.numberOfJoints - 1)
        uPos = 0
        indexing = 1
        for i in range(self.numberOfJoints):
            if uPos > 1.0:
                uPos = 1.0
            if i == ((self.numberOfJoints - 1)/2)-1:
                indexing = 0
            if i <= ((self.numberOfJoints-2) / 2):
                if i == 0:
                    jLabel = f"L_{self.label}_Corner"

                    cinfo = cmds.createNode("pointOnCurveInfo", n=f"UpLip_{i}_cInfo")                    
                    lCorner = cmds.createNode("joint",
                                              n=jLabel)                    
                    cmds.connectAttr(f"{upCurve}.worldSpace[0]", f"{cinfo}.inputCurve")
                    cmds.connectAttr(f"{cinfo}.result.position", f"{lCorner}.translate")
                    cmds.setAttr(f"{cinfo}.parameter", uPos)

                    cornerJoints.append(lCorner)
                    cInfoNodes.append(cinfo)
                # Make Left Joints
                else:
                    jUpLabel = f"L_{self.label}_Up_{i}"
                    jLoLabel = f"L_{self.label}_Lo_{i}"

                    nPos = 0.5 - uPos
                    upcinfo = cmds.createNode("pointOnCurveInfo", n=f"UpLip_{i}_cInfo")                    
                    upJnt = cmds.createNode("joint",
                                              n=jUpLabel)
                    locinfo = cmds.createNode("pointOnCurveInfo", n=f"LoLip_{i}_cInfo")                    
                    loJnt = cmds.createNode("joint",
                                              n=jLoLabel)
                    cmds.connectAttr(f"{upCurve}.worldSpace[0]", f"{upcinfo}.inputCurve")
                    cmds.connectAttr(f"{upcinfo}.result.position", f"{upJnt}.translate")
                    cmds.setAttr(f"{upcinfo}.parameter", nPos)
                    cmds.connectAttr(f"{loCurve}.worldSpace[0]", f"{locinfo}.inputCurve")
                    cmds.connectAttr(f"{locinfo}.result.position", f"{loJnt}.translate")
                    cmds.setAttr(f"{locinfo}.parameter", nPos)

                    upLipJoints.append(upJnt)
                    loLipJoints.append(loJnt)
                    cInfoNodes.append(upcinfo)
                    cInfoNodes.append(locinfo)
                    indexing+=1

            elif i >= ((self.numberOfJoints+1) / 2):
                if i == self.numberOfJoints - 1:
                    jLabel = f"R_{self.label}_Corner"

                    cinfo = cmds.createNode("pointOnCurveInfo", n=f"UpLip_{indexing}_cInfo")                    
                    rCorner = cmds.createNode("joint",
                                              n=jLabel)
                    
                    cmds.connectAttr(f"{upCurve}.worldSpace[0]", f"{cinfo}.inputCurve")
                    cmds.connectAttr(f"{cinfo}.result.position", f"{rCorner}.translate")
                    cmds.setAttr(f"{cinfo}.parameter", uPos)

                    cornerJoints.append(rCorner)
                    cInfoNodes.append(cinfo)
                # Make Right Joints
                else:                    
                    jUpLabel = f"R_{self.label}_Up_{indexing}"
                    jLoLabel = f"R_{self.label}_Lo_{indexing}"

                    upcinfo = cmds.createNode("pointOnCurveInfo", n=f"UpLip_{indexing}_cInfo")                    
                    upJnt = cmds.createNode("joint",
                                              n=jUpLabel)
                    locinfo = cmds.createNode("pointOnCurveInfo", n=f"LoLip_{indexing}_cInfo")                    
                    loJnt = cmds.createNode("joint",
                                              n=jLoLabel)
                    cmds.connectAttr(f"{upCurve}.worldSpace[0]", f"{upcinfo}.inputCurve")
                    cmds.connectAttr(f"{upcinfo}.result.position", f"{upJnt}.translate")
                    cmds.setAttr(f"{upcinfo}.parameter", uPos)
                    cmds.connectAttr(f"{loCurve}.worldSpace[0]", f"{locinfo}.inputCurve")
                    cmds.connectAttr(f"{locinfo}.result.position", f"{loJnt}.translate")
                    cmds.setAttr(f"{locinfo}.parameter", uPos)

                    upLipJoints.append(upJnt)
                    loLipJoints.append(loJnt)
                    cInfoNodes.append(upcinfo)
                    cInfoNodes.append(locinfo)
                    indexing += 1
            else:
                # Make Midde Joint
                jUpLabel = f"M_{self.label}_Up"
                jLoLabel = f"M_{self.label}_Lo"

                upcinfo = cmds.createNode("pointOnCurveInfo", n=f"UpLip_{i}_cInfo")                    
                upJnt = cmds.createNode("joint",
                                            n=jUpLabel)
                locinfo = cmds.createNode("pointOnCurveInfo", n=f"LoLip_{i}_cInfo")                    
                loJnt = cmds.createNode("joint",
                                            n=jLoLabel)
                cmds.connectAttr(f"{upCurve}.worldSpace[0]", f"{upcinfo}.inputCurve")
                cmds.connectAttr(f"{upcinfo}.result.position", f"{upJnt}.translate")
                cmds.setAttr(f"{upcinfo}.parameter", uPos)
                cmds.connectAttr(f"{loCurve}.worldSpace[0]", f"{locinfo}.inputCurve")
                cmds.connectAttr(f"{locinfo}.result.position", f"{loJnt}.translate")
                cmds.setAttr(f"{locinfo}.parameter", uPos)

                upLipJoints.append(upJnt)
                loLipJoints.append(loJnt)
                cInfoNodes.append(upcinfo)
                cInfoNodes.append(locinfo)
            uPos += infl

        # Make position dict
        jPos = {}
        for u, l in zip(upLipJoints, loLipJoints):
            jPos[u] = cmds.xform(u, q=True, ws=True, t=True)
            jPos[l] = cmds.xform(l, q=True, ws=True, t=True)
        jPos[cornerJoints[0]] = cmds.xform(cornerJoints[0], q=True, ws=True, t=True)
        jPos[cornerJoints[1]] = cmds.xform(cornerJoints[1], q=True, ws=True, t=True)
        
        cmds.delete(cInfoNodes)
        cmds.delete([upCurve, loCurve])
        for j, t in jPos.items():
            cmds.xform(j, ws=True, t=t)        

        # Aim Joints.
        lipRange = (len(upLipJoints)-1) / 2

        # Order lists
        orderedUpLipL = upLipJoints[:int(lipRange):]
        orderedUpLipL.insert(0, upLipJoints[int(lipRange)])
        orderedLoLipL = loLipJoints[:int(lipRange):]
        orderedLoLipL.insert(0, loLipJoints[int(lipRange)])
        orderedUpLipR = upLipJoints[int(lipRange)+1::]
        orderedLoLipR = loLipJoints[int(lipRange)+1::]

        # jointTools.aimSequence(targets=orderedUpLipL, upObj=f"{self.side}_{self.label}_UpVector_proxy",
        #                        aimAxis=self.aimAxis, upAxis=self.upAxis, upType="objectrotation", vector=self.upAxis)
        # jointTools.aimSequence(targets=orderedLoLipL, upObj=f"{self.side}_{self.label}_UpVector_proxy",
        #                        aimAxis=self.aimAxis, upAxis=self.upAxis, upType="objectrotation", vector=self.upAxis)
        # jointTools.aimSequence(targets=orderedUpLipR, upObj=f"{self.side}_{self.label}_UpVector_proxy",
        #                        aimAxis=self.aimAxis, upAxis=jointTools.axisFlip(self.upAxis), upType="objectrotation", vector=self.upAxis)        
        # jointTools.aimSequence(targets=orderedLoLipR, upObj=f"{self.side}_{self.label}_UpVector_proxy",
        #                        aimAxis=self.aimAxis, upAxis=jointTools.axisFlip(self.upAxis), upType="objectrotation", vector=self.upAxis)
        oc = cmds.orientConstraint([upLipJoints[int(lipRange)-1], loLipJoints[int(lipRange)-1]], cornerJoints[0], mo=0)[0]
        cmds.setAttr(f"{oc}.interpType", 2)
        cmds.delete(oc)
        oc = cmds.orientConstraint([upLipJoints[int(lipRange)+1], loLipJoints[int(lipRange)+1]], cornerJoints[1], mo=0)[0]
        cmds.setAttr(f"{oc}.interpType", 2)
        cmds.delete(oc)
        cmds.makeIdentity(upLipJoints, a=True)
        cmds.makeIdentity(loLipJoints, a=True)
        cmds.makeIdentity(cornerJoints, a=True)     

        # components
        upParents = []
        upOffsets = []
        upCtrls = []
        loParents = []
        loOffsets = []
        loCtrls = []
        cornerParents = []
        cornerOffsets = []
        cornerCtrls = []
        ptcs = []

        # Make control and logic.
        for upJnt, loJnt in zip(upLipJoints, loLipJoints):
            # Make parent, offset, control
            upPar = cmds.createNode("transform", n=f"{upJnt}_grp")
            upOffset = cmds.createNode("transform", n=f"{upJnt}_offset", p=upPar)
            upCtrl = cmds.createNode("transform", n=f"{upJnt}_CTRL", p=upOffset)
            cmds.xform(upPar, ws=True, m=cmds.xform(upJnt, q=True, ws=True, m=True))
            loPar = cmds.createNode("transform", n=f"{loJnt}_grp")
            loOffset = cmds.createNode("transform", n=f"{loJnt}_offset", p=loPar)
            loCtrl = cmds.createNode("transform", n=f"{loJnt}_CTRL", p=loOffset)
            cmds.xform(loPar, ws=True, m=cmds.xform(loJnt, q=True, ws=True, m=True))

            ptc_u = cmds.parentConstraint(upCtrl, upJnt, mo=0, n=f"{upJnt}_ptc")[0]
            cmds.setAttr(f"{ptc_u}.interpType", 2)
            ptc_l = cmds.parentConstraint(loCtrl, loJnt, mo=0, n=f"{loJnt}_ptc")[0]
            cmds.setAttr(f"{ptc_l}.interpType", 2)

            ptcs.append(ptc_u)
            ptcs.append(ptc_l)
            up = ctrlCrv.Ctrl(
            node=upCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.75, self.ctrlScale[2] * 0.75],
            offset=[0, 0, 0]
            )
            up.giveCtrlShape()
            lo = ctrlCrv.Ctrl(
            node=loCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.75, self.ctrlScale[2] * 0.75],
            offset=[0, 0, 0]
            )
            lo.giveCtrlShape()
            
            upParents.append(upPar)
            upOffsets.append(upOffset)
            upCtrls.append(upCtrl)
            loParents.append(loPar)
            loOffsets.append(loOffset)
            loCtrls.append(loCtrl)


        for corner in cornerJoints:
            par = cmds.createNode("transform", n=f"{corner}_grp")
            offset = cmds.createNode("transform", n=f"{corner}_offset", p=par)
            ctrl = cmds.createNode("transform", n=f"{corner}_CTRL", p=offset)
            cmds.xform(par, ws=True, m=cmds.xform(corner, q=True, ws=True, m=True))
            ptc = cmds.parentConstraint(ctrl, corner, mo=0, n=f"{corner}_ptc")[0]
            cmds.setAttr(f"{ptc}.interpType", 2)
            ptcs.append(ptc)

            cornerParents.append(par)
            cornerOffsets.append(offset)
            cornerCtrls.append(ctrl)
            crnr = ctrlCrv.Ctrl(
            node=ctrl,
            shape="sphere",
            scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.75, self.ctrlScale[2] * 0.75],
            offset=[0, 0, 0]
            )
            crnr.giveCtrlShape()
        for up, lp in zip(upParents[int(lipRange+1)::], loParents[int(lipRange+1)::]):
            cmds.setAttr(f"{up}.scaleX", -1)
            cmds.setAttr(f"{lp}.scaleX", -1)
        cmds.setAttr(f"{cornerParents[1]}.scaleX", -1)

        # Side Inversion
        lGroup = cmds.createNode("transform", n=f"L_{self.label}_controls")
        rGroup = cmds.createNode("transform", n=f"R_{self.label}_controls")
        cmds.parent(upParents[:int(lipRange):], lGroup)
        cmds.parent(loParents[:int(lipRange):], lGroup)
        cmds.parent(cornerParents[0], lGroup)
        cmds.setAttr(f"{rGroup}.scaleX", -1)
        cmds.parent(upParents[int(lipRange+1)::], rGroup)
        cmds.parent(loParents[int(lipRange+1)::], rGroup)
        cmds.parent(cornerParents[1], rGroup)

        # Make constraints
        upMiddlePar = cmds.createNode("transform", n=f"{upLipJoints[int(lipRange)]}_Main_grp")
        upMiddleCtrl = cmds.createNode("transform", n=f"{upLipJoints[int(lipRange)]}_Main_CTRL", p=upMiddlePar)
        loMiddlePar = cmds.createNode("transform", n=f"{loLipJoints[int(lipRange)]}_Main_grp")
        loMiddleCtrl = cmds.createNode("transform", n=f"{loLipJoints[int(lipRange)]}_Main_CTRL", p=loMiddlePar)
        lCornerPar = cmds.createNode("transform", n=f"{cornerJoints[0]}_Main_grp")
        lCornerCtrl = cmds.createNode("transform", n=f"{cornerJoints[0]}_Main_CTRL", p=lCornerPar)
        rCornerPar = cmds.createNode("transform", n=f"{cornerJoints[1]}_Main_grp")
        rCornerCtrl = cmds.createNode("transform", n=f"{cornerJoints[1]}_Main_CTRL", p=rCornerPar)
        um = ctrlCrv.Ctrl(
            node=upMiddleCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
            offset=[0, 0, 0]
            )
        um.giveCtrlShape()
        lm = ctrlCrv.Ctrl(
            node=loMiddleCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
            offset=[0, 0, 0]
            )
        lm.giveCtrlShape()
        lc = ctrlCrv.Ctrl(
            node=lCornerCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
            offset=[0, 0, 0]
            )
        lc.giveCtrlShape()
        rc = ctrlCrv.Ctrl(
            node=rCornerCtrl,
            shape="sphere",
            scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
            offset=[0, 0, 0]
            )
        rc.giveCtrlShape()

        cmds.xform(upMiddlePar, ws=True, t=cmds.xform(upLipJoints[int(lipRange)], q=True, ws=True, t=True))
        cmds.xform(loMiddlePar, ws=True, t=cmds.xform(loLipJoints[int(lipRange)], q=True, ws=True, t=True))
        cmds.xform(lCornerPar, ws=True, t=cmds.xform(cornerJoints[0], q=True, ws=True, t=True))
        cmds.xform(rCornerPar, ws=True, t=cmds.xform(cornerJoints[1], q=True, ws=True, t=True))
        cmds.setAttr(f"{rCornerPar}.scaleX", -1)

        cmds.parent(lCornerPar, lGroup)
        cmds.parent(rCornerPar, rGroup)

        ptc = cmds.parentConstraint(upMiddleCtrl, upParents[int(lipRange)], mo=1, n=f"{upParents[int(lipRange)]}_ptc")
        ptc = cmds.parentConstraint(loMiddleCtrl, loParents[int(lipRange)], mo=1, n=f"{loParents[int(lipRange)]}_ptc")
        ptc = cmds.parentConstraint(lCornerCtrl, cornerParents[0], mo=1, n=f"{cornerParents[0]}_ptc")
        ptc = cmds.parentConstraint(rCornerCtrl, cornerParents[1], mo=1, n=f"{cornerParents[1]}_ptc")

        # Oh for fucks sake. Ok, make list starting with M control, reverse list for R side. 
        upLOffsets = upOffsets[:int(lipRange):]
        upLOffsets.insert(0, upOffsets[int(lipRange)])
        loLOffsets = loOffsets[:int(lipRange):]
        loLOffsets.insert(0, loOffsets[int(lipRange)])
        upROffsets = upOffsets[int(lipRange)+1::]
        upROffsets.insert(0, upOffsets[int(lipRange)])
        loROffsets = loOffsets[int(lipRange)+1::]
        loROffsets.insert(0, loOffsets[int(lipRange)])
        acs = []
        for i in range(len(upLOffsets)-1):
            ac_ul = cmds.aimConstraint(upLOffsets[i], upLOffsets[i+1], mo=0, 
                                    n=f"{upLOffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
                                    u=jointTools.axisToVector(self.upAxis), wuo=upLOffsets[i], wut="object")[0]
            ac_ll = cmds.aimConstraint(loLOffsets[i], loLOffsets[i+1], mo=0, 
                                    n=f"{loLOffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
                                    u=jointTools.axisToVector(self.upAxis), wuo=loLOffsets[i], wut="object")[0]
            ac_ur = cmds.aimConstraint(upROffsets[i], upROffsets[i+1], mo=0, 
                                    n=f"{upROffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
                                    u=jointTools.axisToVector(jointTools.axisFlip(self.upAxis)), wuo=upROffsets[i], wut="object")[0]
            ac_lr = cmds.aimConstraint(loROffsets[i], loROffsets[i+1], mo=0 , 
                                    n=f"{loROffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
                                    u=jointTools.axisToVector(jointTools.axisFlip(self.upAxis)), wuo=loROffsets[i], wut="object")[0]
            acs.extend([ac_ul, ac_ll, ac_ur, ac_lr])
        cmds.delete(acs)
        cmds.delete(ptcs)
        cmds.makeIdentity(upLipJoints, a=True)
        cmds.makeIdentity(loLipJoints, a=True)
        cmds.makeIdentity(cornerJoints, a=True)
        
        for i in range(len(upLipJoints)):# zip(upLipJoints, loLipJoints):
            ptc = cmds.parentConstraint(upCtrls[i], upLipJoints[i], mo=0, n=f"{upLipJoints[i]}_ptc")[0]
            cmds.setAttr(f"{ptc}.interpType", 2)
            ptc = cmds.parentConstraint(loCtrls[i], loLipJoints[i], mo=0, n=f"{loLipJoints[i]}_ptc")[0]
            cmds.setAttr(f"{ptc}.interpType", 2)
        for i in range(2):
            ptc = cmds.parentConstraint(cornerCtrls[i], cornerJoints[i], n=f"{cornerJoints[i]}_ptc", mo=0)
        for i in range(len(upLOffsets)-1):
            ac_ul = cmds.aimConstraint(upLOffsets[i], upLOffsets[i+1], mo=0, 
                                    n=f"{upLOffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
                                    u=jointTools.axisToVector(self.upAxis), wuo=upLOffsets[i], wut="object")[0]
            ac_ll = cmds.aimConstraint(loLOffsets[i], loLOffsets[i+1], mo=0, 
                                    n=f"{loLOffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
                                    u=jointTools.axisToVector(self.upAxis), wuo=loLOffsets[i], wut="object")[0]
            ac_ur = cmds.aimConstraint(upROffsets[i], upROffsets[i+1], mo=0, 
                                    n=f"{upROffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
                                    u=jointTools.axisToVector(jointTools.axisFlip(self.upAxis)), wuo=upROffsets[i], wut="object")[0]
            ac_lr = cmds.aimConstraint(loROffsets[i], loROffsets[i+1], mo=0 , 
                                    n=f"{loROffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
                                    u=jointTools.axisToVector(jointTools.axisFlip(self.upAxis)), wuo=loROffsets[i], wut="object")[0]

        inflCalc = 0.0
        inflVal = 1 / (lipRange+1)

        for i in range(int(lipRange)):
            inflCalc +=inflVal
            # Make lip MD / PMA
            mlUpMd = cmds.createNode("multiplyDivide", n=f"{upLipJoints[:int(lipRange):][i]}_M_MD")
            lUpMd = cmds.createNode("multiplyDivide", n=f"{upLipJoints[:int(lipRange):][i]}_L_MD")
            lUpPma = cmds.createNode("plusMinusAverage", n=f"{upLipJoints[:int(lipRange):][i]}_PMA")
            mlLoMd = cmds.createNode("multiplyDivide", n=f"{loLipJoints[:int(lipRange):][i]}_M_MD")
            lLoMd = cmds.createNode("multiplyDivide", n=f"{loLipJoints[:int(lipRange):][i]}_L_MD")
            lLoPma = cmds.createNode("plusMinusAverage", n=f"{upLipJoints[:int(lipRange):][i]}_PMA")
            mrUpMd = cmds.createNode("multiplyDivide", n=f"{upLipJoints[:int(lipRange):-1][i]}_M_MD")
            rUpMd = cmds.createNode("multiplyDivide", n=f"{upLipJoints[:int(lipRange):-1][i]}_R_MD")
            rUpPma = cmds.createNode("plusMinusAverage", n=f"{upLipJoints[:int(lipRange):-1][i]}_PMA")
            mrLoMd = cmds.createNode("multiplyDivide", n=f"{loLipJoints[:int(lipRange):-1][i]}_M_MD")
            rLoMd = cmds.createNode("multiplyDivide", n=f"{loLipJoints[:int(lipRange):-1][i]}_R_MD")
            rLoPma = cmds.createNode("plusMinusAverage", n=f"{upLipJoints[:int(lipRange):-1][i]}_PMA")
            
            # Connect Attributes
            # Up Left Attr Connections
            cmds.connectAttr(f"{upMiddleCtrl}.translate", f"{mlUpMd}.input1")
            cmds.connectAttr(f"{lCornerCtrl}.translate", f"{lUpMd}.input1")
            cmds.connectAttr(f"{mlUpMd}.output", f"{lUpPma}.input3D[0]")
            cmds.connectAttr(f"{lUpMd}.output", f"{lUpPma}.input3D[1]")
            cmds.connectAttr(f"{lUpPma}.output3D", f"{upOffsets[:int(lipRange):][i]}.translate")
            # Lo Left Attr Connections
            cmds.connectAttr(f"{loMiddleCtrl}.translate", f"{mlLoMd}.input1")
            cmds.connectAttr(f"{lCornerCtrl}.translate", f"{lLoMd}.input1")
            cmds.connectAttr(f"{mlLoMd}.output", f"{lLoPma}.input3D[0]")
            cmds.connectAttr(f"{lLoMd}.output", f"{lLoPma}.input3D[1]")
            cmds.connectAttr(f"{lLoPma}.output3D", f"{loOffsets[:int(lipRange):][i]}.translate")
            # Up Right Attr Connections
            cmds.connectAttr(f"{upMiddleCtrl}.translate", f"{mrUpMd}.input1")
            cmds.connectAttr(f"{rCornerCtrl}.translate", f"{rUpMd}.input1")
            cmds.connectAttr(f"{mrUpMd}.output", f"{rUpPma}.input3D[0]")
            cmds.connectAttr(f"{rUpMd}.output", f"{rUpPma}.input3D[1]")
            cmds.connectAttr(f"{rUpPma}.output3D", f"{upOffsets[int(lipRange)+1::][i]}.translate")
            # Lo Right Attr Connections
            cmds.connectAttr(f"{loMiddleCtrl}.translate", f"{mrLoMd}.input1")
            cmds.connectAttr(f"{rCornerCtrl}.translate", f"{rLoMd}.input1")
            cmds.connectAttr(f"{mrLoMd}.output", f"{rLoPma}.input3D[0]")
            cmds.connectAttr(f"{rLoMd}.output", f"{rLoPma}.input3D[1]")
            cmds.connectAttr(f"{rLoPma}.output3D", f"{loOffsets[int(lipRange)+1::][i]}.translate")

            # Set Calc Values
            sine = self.easeInCubic(input=inflCalc)
            cubicIn = self.easeInCubic(input=inflCalc)
            sineIn = self.easeInSine(input=inflCalc)

            # Up Left
            cmds.setAttr(f"{mlUpMd}.input2.input2X", 1.0-sineIn)
            cmds.setAttr(f"{mlUpMd}.input2.input2Y", (1.0-cubicIn))
            cmds.setAttr(f"{mlUpMd}.input2.input2Z", (1.0-cubicIn))
            cmds.setAttr(f"{lUpMd}.input2.input2X", sineIn)
            cmds.setAttr(f"{lUpMd}.input2.input2Y", (cubicIn))
            cmds.setAttr(f"{lUpMd}.input2.input2Z", (cubicIn))
            # Lo Left
            cmds.setAttr(f"{mlLoMd}.input2.input2X", 1.0-sineIn)
            cmds.setAttr(f"{mlLoMd}.input2.input2Y", (1.0-cubicIn))
            cmds.setAttr(f"{mlLoMd}.input2.input2Z", (1.0-cubicIn))
            cmds.setAttr(f"{lLoMd}.input2.input2X", sineIn)
            cmds.setAttr(f"{lLoMd}.input2.input2Y", (cubicIn))
            cmds.setAttr(f"{lLoMd}.input2.input2Z", (cubicIn))
            # Up Right
            cmds.setAttr(f"{mrUpMd}.input2.input2X", (1.0-sineIn)*-1)
            cmds.setAttr(f"{mrUpMd}.input2.input2Y", (1.0-cubicIn))
            cmds.setAttr(f"{mrUpMd}.input2.input2Z", 1.0-cubicIn)
            cmds.setAttr(f"{rUpMd}.input2.input2X", (sineIn))
            cmds.setAttr(f"{rUpMd}.input2.input2Y", (cubicIn))
            cmds.setAttr(f"{rUpMd}.input2.input2Z", cubicIn)
            # Lo Right
            cmds.setAttr(f"{mrLoMd}.input2.input2X", (1.0-sineIn)*-1)
            cmds.setAttr(f"{mrLoMd}.input2.input2Y", (1.0-cubicIn))
            cmds.setAttr(f"{mrLoMd}.input2.input2Z", 1.0-cubicIn)
            cmds.setAttr(f"{rLoMd}.input2.input2X", (sineIn))
            cmds.setAttr(f"{rLoMd}.input2.input2Y", (cubicIn))
            cmds.setAttr(f"{rLoMd}.input2.input2Z", cubicIn)

        self.addSocketMetaData()

    def easeInOutSine(self, input = 1.0):
        return -(m.cos(m.pi * input) - 1.0) / 2.0

    def easeOutCubic(self, input = 1.0):
        return 1 - m.pow(1.0 - input, 3.0)
    
    def easeInCubic(self, input = 1.0):
        return input * input * input
    
    def easeInCirc(self, input = 1.0):
        return 1 - m.sqrt(1 - m.pow(input, 2))
    
    def easeInSine(self, input = 1.0):
        return 1 - m.cos((input*m.pi)/2)
    
