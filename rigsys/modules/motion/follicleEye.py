"""Lip Motion Module."""


import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds
import math as m


class FollicleEye(motionBase.MotionModuleBase):
    """Root Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, numberOfJoints: int = 5, 
                 lidSegments: int = 3, follicleMesh: str = None, follicleSurface: str = None, eyeball: bool = True,
                 buildOrder: int = 2000, 
                 isMuted: bool = False, parent: str = None, mirror: bool = False, bypassProxiesOnly: bool = True, 
                 selectedPlug: str = "", selectedSocket: str = "", aimAxis: str = "+x", upAxis: str = "-z") -> None:
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

              

        NOTE NOTE NOTE NOTE NOTE ATTENTION ATTENTION: ZIPPER DEBUG...
        TODO: 
        New Heirarchy for lip controls
        GROUP
            Offset 
            ZipperOffset: A node that has the positional / rotational initial data of the Offset
                Zipper
                    CTRL
        
            Locator: A node that has the positional / rotational initial data of the Offset
        
        1: Mult Matrix the WorldSpace of the Offset and InverseWorldSpace then decompose the matrix to xform Data
        2: Take the Transoform and Rotate data then put them into two Multiply Divide nodes in Input 1
        3: Create a Remap Value node and a zipper / lip influence value on the Mouth CTRL
        4: lip Influence > Input Value, use the out value as a multiplier for the Input 2 of each MultiplyDivide node
        5: Output of the MD nodes to Translate / Rotate of the Zipper Node. 

        The input min / max of the remap value will dictate the zipper falloff. Do this in pairs of values IE L_Up_1 and R_Up_1        
        '''

        if ctrlScale is None:
            ctrlScale = [1.0, 1.0, 1.0]

        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        self.lidSegments = lidSegments
        self.numberOfJoints = numberOfJoints
        self.follicleMesh = follicleMesh
        self.follicleSurface = follicleSurface
        self.eyeball = eyeball
        self.lidProxies = []
        self.upLidProxies = []
        self.loLidProxies = []
        

        self.proxies = {
            "Eyeball": proxy.Proxy(
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name="Eyeball"
            )
        }
        # Duplicate a full lip range or a half lip range for proxies? Probably full... how to?
        if self.lidSegments < 3:
            self.lidSegments = 3
        if self.lidSegments >= 3:
            # Manually override lid segments to be 3 for now; adjust in a future update
            # self.lidSegments = 3
            
            par = "Eyeball"
            self.proxies["Up"] = proxy.Proxy(
                        position=[0, 0.25, 0],
                        rotation=[0, 0, 0],
                        side=self.side,
                        label=self.label,
                        name="Up",
                        parent=par
                    )
            self.proxies["Lo"] = proxy.Proxy(
                        position=[0, -0.25, 0],
                        rotation=[0, 0, 0],
                        side=self.side,
                        label=self.label,
                        name="Lo",
                        parent=par
                    )
            
            self.lidProxies.append(f"{self.side}_{self.label}_M_Up{self.label}")
            self.lidProxies.append(f"{self.side}_{self.label}_M_Lo{self.label}")
            for i in range(0, self.lidSegments+1):
                upLabel = f"Up_{i}"
                loLabel = f"Lo_{i}"
                inLabel = f"In"
                outLabel = f"Out"
                
                if i > 0:
                    if i != self.lidSegments:
                        self.proxies[upLabel] = proxy.Proxy(
                            position=[i, 0.25, 0],
                            rotation=[0, 0, 0],
                            side=self.side,
                            label=self.label,
                            name=upLabel,
                            parent="Eyeball"
                        )
                        self.proxies[loLabel] = proxy.Proxy(
                            position=[i, -0.25, 0],
                            rotation=[0, 0, 0],
                            side=self.side,
                            label=self.label,
                            name=loLabel,
                            parent="Eyeball"
                        )
                        self.upLidProxies.append(upLabel)
                        self.loLidProxies.append(loLabel)
                    else:
                        self.proxies[inLabel] = proxy.Proxy(
                            position=[i, 0, 0],
                            rotation=[0, 0, 0],  
                            side=self.side,
                            label=self.label,
                            name=inLabel,
                            parent="Eyeball"
                        )
                        self.proxies[outLabel] = proxy.Proxy(
                            position=[i*-1, 0, 0],
                            rotation=[0, 0, 0],
                            side=self.side,
                            label=self.label,
                            name=outLabel,
                            parent="Eyeball"
                        )
                        self.lidProxies.append(inLabel)
                        self.lidProxies.append(outLabel)
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
        plugPosition = self.proxies["Eyeball"].position
        plugRotation = self.proxies["Eyeball"].rotation
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

        # Lists generated for corner to corner up and lo proxies. 
        fullRangeUp = []
        fullRangeUpLabels = []
        fullRangeLo = []
        fullRangeLoLabels = []
        fullRangeUp.append(f"{self.lidProxies[2]}_proxy")
        fullRangeLo.append(f"{self.lidProxies[2]}_proxy")
        fullRangeUpLabels.append(self.lidProxies[2])
        fullRangeLoLabels.append(self.lidProxies[2])
        for up, lo in zip(self.upLidProxies, self.loLidProxies): 
            uProxy = f"{up}_proxy"
            lProxy = f"{lo}_proxy"
            fullRangeUp.append(uProxy)
            fullRangeLo.append(lProxy)
            fullRangeUpLabels.append(up)
            fullRangeLoLabels.append(lo)
        fullRangeUp.append(f"{self.lidProxies[3]}_proxy")
        fullRangeLo.append(f"{self.lidProxies[3]}_proxy")
        fullRangeUpLabels.append(self.lidProxies[3])
        fullRangeLoLabels.append(self.lidProxies[3])

        # # proxy points in list corner to corner for curve generation
        # upRangePoints = []
        # loRangePoints = []
        # for up, lo in zip(fullRangeUp, fullRangeLo): # Making points for curve gen
        #     upLabel = f"{self.side}_{self.label}_{up}"
        #     loLabel = f"{self.side}_{self.label}_{lo}"
        #     upRangePoints.append(cmds.xform(upLabel, q=True, ws=True, t=True))
        #     loRangePoints.append(cmds.xform(loLabel, q=True, ws=True, t=True))

        # upCurve = cmds.curve(n="upLidCurve_TEMP", p=upRangePoints, d=1) # Make curve, rebuild so its a 0-1 param range
        # cmds.rebuildCurve(upCurve, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(self.lidSegments), d=3, ch=False)

        # loCurve = cmds.curve(n="loLidCurve_TEMP", p=loRangePoints, d=1) # Make curve, rebuild so its a 0-1 param range
        # cmds.rebuildCurve(loCurve, rpo=1, rt=0, end=1, kr=0, kcp=0, kep=1, kt=1, s=(self.lidSegments), d=3, ch=False)
        # cmds.error("DEBUG TESTING")
        # Add to joints if even so we have a middle lip point
        # if self.numberOfJoints % 2 == 0:
        #     self.numberOfJoints += 1

        cornerJoints = [] # For corners, 0 In, 1 Out
        upLidJoints = [] # All up lips minus the corners
        loLidJoints = [] # All lo lips minus the corners

        # Making joints from proxy positions. 
        index = 1
        for u, l in zip(fullRangeUpLabels[1:-1:], fullRangeLoLabels[1:-1:]):
            uLabel = f"{self.side}_{self.label}_{u}"
            lLabel = f"{self.side}_{self.label}_{l}"
            uJnt = cmds.createNode("joint", n=uLabel)
            lJnt = cmds.createNode("joint", n=lLabel)

            cmds.xform(uJnt, ws=True, t=cmds.xform(
                f"{self.side}_{self.label}_{fullRangeUp[index]}", q=True, ws=True, t=True
            ))
            cmds.xform(lJnt, ws=True, t=cmds.xform(
                f"{self.side}_{self.label}_{fullRangeLo[index]}", q=True, ws=True, t=True
            ))

            upLidJoints.append(uJnt)
            loLidJoints.append(lJnt)
            index+=1
        
        inLabel = f"{self.side}_{self.label}_{fullRangeUpLabels[0]}"
        outLabel = f"{self.side}_{self.label}_{fullRangeUpLabels[-1]}"
        iJnt = cmds.createNode("joint", n=inLabel)
        oJnt = cmds.createNode("joint", n=outLabel)
        cornerJoints.extend([iJnt, oJnt])
        cmds.xform(iJnt, ws=True, t=cmds.xform(
                f"{self.side}_{self.label}_{fullRangeUp[0]}", q=True, ws=True, t=True
            ))
        cmds.xform(oJnt, ws=True, t=cmds.xform(
                f"{self.side}_{self.label}_{fullRangeUp[-1]}", q=True, ws=True, t=True
            ))

        eyejoint = cmds.createNode("joint", n=f"{self.side}_{self.label}_{self.proxies['Eyeball'].name}")
        cmds.xform(eyejoint, ws=True, t=cmds.xform(
                f"{self.side}_{self.label}_{self.proxies['Eyeball'].name}_proxy", q=True, ws=True, t=True
            ))
        '''
        # Next steps are to make controls and offsets
        # We want the Main Controls to move the local control offsets at a cubic curve
        # We also want another offset to make the local controls slide across a mesh surface
        # Since we want to be able to move the eyelids off the surface... we want the order to be as follows
        MAIN
        ctrl group
        ctrl

        LOCAL
        ctrl group
        follicle offset
        cubic offset
        ctrl
        '''
        upGroups = []
        loGroups = []
        upFolOffsets = []
        loFolOffsets = []
        upEasingOffsets = []
        loEasingOffsets = []
        upControls = []
        loControls = []
        cornerGroups = []
        cornerFolOffsets = []
        cornerEasingOffsets = []
        cornerControls = []

        # Create controls, offsets, ctrl shapes, and lists
        for u, l in zip(upLidJoints, loLidJoints):
            uGrp = cmds.createNode("transform", n=f"{u}_grp")
            lGrp = cmds.createNode("transform", n=f"{l}_grp")
            uFolOffset = cmds.createNode("transform", n=f"{u}_folOffset", p=uGrp)
            lFolOffset = cmds.createNode("transform", n=f"{l}_folOffset", p=lGrp)
            uEaseOffset = cmds.createNode("transform", n=f"{u}_easeOffset", p=uFolOffset)
            lEaseOffset = cmds.createNode("transform", n=f"{l}_easeOffset", p=lFolOffset)
            uCtrl = cmds.createNode("transform", n=f"{u}_CTRL", p=uEaseOffset)
            lCtrl = cmds.createNode("transform", n=f"{l}_CTRL", p=lEaseOffset)
            uCtrlShape = ctrlCrv.Ctrl(
                node=uCtrl,
                shape="sphere",
                scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.75, self.ctrlScale[2] * 0.75],
                offset=[0, 0, 0]
            )
            uCtrlShape.giveCtrlShape()
            lCtrlShape = ctrlCrv.Ctrl(
                node=lCtrl,
                shape="sphere",
                scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.75, self.ctrlScale[2] * 0.75],
                offset=[0, 0, 0]
            )
            lCtrlShape.giveCtrlShape()

            upGroups.append(uGrp)
            loGroups.append(lGrp)
            upFolOffsets.append(uFolOffset)
            loFolOffsets.append(lFolOffset)
            upEasingOffsets.append(uEaseOffset)
            loEasingOffsets.append(lEaseOffset)
            upControls.append(uCtrl)
            loControls.append(lCtrl)
            cmds.xform(uGrp, ws=True, t=cmds.xform(
                u, q=True, ws=True, t=True
            ))
            cmds.xform(lGrp, ws=True, t=cmds.xform(
                l, q=True, ws=True, t=True
            ))

        for c in cornerJoints:
            cGrp = cmds.createNode("transform", n=f"{c}_grp")
            cFolOffset = cmds.createNode("transform", n=f"{c}_folOffset", p=cGrp)
            cEaseOffset = cmds.createNode("transform", n=f"{c}_easeOffset", p=cFolOffset)
            cCtrl = cmds.createNode("transform", n=f"{c}_CTRL", p=cEaseOffset)
            cCtrlShape = ctrlCrv.Ctrl(
                node=cCtrl,
                shape="sphere",
                scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.75, self.ctrlScale[2] * 0.75],
                offset=[0, 0, 0]
            )
            cCtrlShape.giveCtrlShape()

            cornerGroups.append(cGrp)
            cornerFolOffsets.append(cFolOffset)
            cornerEasingOffsets.append(cEaseOffset)
            cornerControls.append(cCtrl)
            cmds.xform(cGrp, ws=True, t=cmds.xform(
                c, q=True, ws=True, t=True
            ))

        # Make Main controls
        upLidGrp = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['Up'].name}_Main_grp")
        loLidGrp = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['Lo'].name}_Main_grp")
        upLidCtrl = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['Up'].name}_Main_CTRL", p=upLidGrp)
        loLidCtrl = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['Lo'].name}_Main_CTRL", p=loLidGrp)

        inLidGrp = cmds.createNode("transform", n=f"{cornerJoints[0]}_Main_grp")
        outLidGrp = cmds.createNode("transform", n=f"{cornerJoints[1]}_Main_grp")
        inLidCtrl = cmds.createNode("transform", n=f"{cornerJoints[0]}_Main_CTRL", p=inLidGrp)
        outLidCtrl = cmds.createNode("transform", n=f"{cornerJoints[1]}_Main_CTRL", p=outLidGrp)

        # upRangeFolOffsets = []
        # loRangeFolOffsets = []
        # upRangeEaseOffsets = []
        # loRangeEaseOffsets = []
        # upRangeFolOffsets.append(cornerFolOffsets)
        useMesh = False
        buildFollicles = False
        if self.follicleMesh != None:
            if cmds.objExists(self.follicleMesh):
                useMesh = True
                buildFollicles = True
        elif self.follicleSurface != None:
            if useMesh == True:
                pass
            else:
                if cmds.objExists(self.follicleSurface):
                    useMesh = False
                    buildFollicles = True

        if buildFollicles:
            index = 0
            for uf, lf in zip(upFolOffsets, loFolOffsets):
                ufol = cmds.createNode("transform", n=f"{upLidJoints[index]}_fol")
                ufolShape = cmds.createNode("follicle", n=f"{upLidJoints[index]}_folShape", p=ufol)
                lfol = cmds.createNode("transform", n=f"{loLidJoints[index]}_fol")
                lfolShape = cmds.createNode("follicle", n=f"{loLidJoints[index]}_folShape", p=lfol)
                cmds.setAttr(f"{ufolShape}.visibility", 0, l=True, k=False)
                cmds.setAttr(f"{lfolShape}.visibility", 0, l=True, k=False)
                if useMesh:
                    # UP
                    ucpom = cmds.createNode("closestPointOnMesh", n=f"{uf}_CPOM")
                    cmds.connectAttr(
                        f"{self.follicleMesh}.worldMatrix[0]", f"{ufolShape}.inputWorldMatrix", f=True)
                    cmds.connectAttr(f"{self.follicleMesh}.outMesh",
                                    f"{ufolShape}.inputMesh", f=True)
                    # ucpom connections
                    uDM = cmds.createNode("decomposeMatrix", n=f"{upGroups[index]}_DM")
                    cmds.connectAttr(f"{upGroups[index]}.worldMatrix[0]", f"{uDM}.inputMatrix")
                    cmds.connectAttr(f"{uDM}.outputTranslate", f"{ucpom}.inPosition")
                    cmds.connectAttr(f"{ucpom}.parameterU", f"{ufolShape}.parameterU")
                    cmds.connectAttr(f"{ucpom}.parameterV", f"{ufolShape}.parameterV")
                    cmds.connectAttr(f"{ufolShape}.outTranslate", f"{ufol}.translate")
                    cmds.connectAttr(f"{ufolShape}.outRotate", f"{ufol}.rotate")
                    # cmds.connectAttr(f"{ufol}.translate", f"{uf}.translate")
                    
                    cmds.connectAttr(f"{self.follicleMesh}.outMesh", f"{ucpom}.inMesh")
                    cmds.connectAttr(f"{self.follicleMesh}.worldMatrix[0]", f"{ucpom}.inputMatrix")
                    pc = cmds.pointConstraint(ufol, uf, mo=1)
                    
                    # LO
                    lcpom = cmds.createNode("closestPointOnMesh", n=f"{lf}_CPOM")
                    cmds.connectAttr(
                        f"{self.follicleMesh}.worldMatrix[0]", f"{lfolShape}.inputWorldMatrix", f=True)
                    cmds.connectAttr(f"{self.follicleMesh}.outMesh",
                                    f"{lfolShape}.inputMesh", f=True)
                    # ucpom connections
                    lDM = cmds.createNode("decomposeMatrix", n=f"{loGroups[index]}_DM")
                    cmds.connectAttr(f"{loGroups[index]}.worldMatrix[0]", f"{lDM}.inputMatrix")
                    cmds.connectAttr(f"{lDM}.outputTranslate", f"{lcpom}.inPosition")
                    cmds.connectAttr(f"{lcpom}.parameterU", f"{lfolShape}.parameterU")
                    cmds.connectAttr(f"{lcpom}.parameterV", f"{lfolShape}.parameterV")
                    cmds.connectAttr(f"{lfolShape}.outTranslate", f"{lfol}.translate")
                    cmds.connectAttr(f"{lfolShape}.outRotate", f"{lfol}.rotate")
                    # cmds.connectAttr(f"{ufol}.translate", f"{uf}.translate")
                    
                    cmds.connectAttr(f"{self.follicleMesh}.outMesh", f"{lcpom}.inMesh")
                    cmds.connectAttr(f"{self.follicleMesh}.worldMatrix[0]", f"{lcpom}.inputMatrix")
                    pc = cmds.pointConstraint(lfol, lf, mo=1)
                else: # Ill do this later...
                    ucpos = cmds.createNode("closestPointOnSurface", n=f"{uf}_CPOS")
                    cmds.connectAttr(
                        f"{self.follicleSurface}.worldMatrix[0]", f"{ufolShape}.inputWorldMatrix", f=True)
                    cmds.connectAttr(f"{self.follicleSurface}.local",
                                    f"{ufolShape}.inputSurface", f=True)
                    
                    # ucpom connections
                    uDM = cmds.createNode("decomposeMatrix", n=f"{upGroups[index]}_DM")
                    cmds.connectAttr(f"{upGroups[index]}.worldMatrix[0]", f"{uDM}.inputMatrix")
                    cmds.connectAttr(f"{uDM}.outputTranslate", f"{ucpos}.inPosition")
                    cmds.connectAttr(f"{ucpos}.parameterU", f"{ufolShape}.parameterU")
                    cmds.connectAttr(f"{ucpos}.parameterV", f"{ufolShape}.par")
                index+=1


        '''
        EXAMPLE
        import maya.cmds as cmds

        testList = ["In", "1", "2", "3", "4", "Out"]
        listLen = len(testList)
        if len(testList) % 2 == 0:
            print("EVEN")
        else:
            print("ODD")
            lenList-=1
        halfLen = listLen / 2
        inflRate = 1 / (halfLen - 1)
        inflVal = 0.0

        for i in testList:
            
            if inflVal >=1.0:
                inflVal = 1.0
                
            print(f"TARGET: {i}   VALUE:{inflVal}")
            
            
            if i in testList[int(halfLen)::]:
                inflVal-=inflRate
            else:
                inflVal+=inflRate


        # Build Follicles
        fol = cmds.createNode(
            "transform", n=f"{self.side}_{self.label}_{i}_fol")
        folShape = cmds.createNode(
            "follicle", n=f"{self.side}_{self.label}_{i}_folShape", p=fol)
        cmds.setAttr(f"{folShape}.visibility", 0, l=True, k=False)
        cmds.connectAttr(
            f"{metaRibbon}.worldMatrix[0]", f"{folShape}.inputWorldMatrix", f=True)
        cmds.connectAttr(f"{metaRibbon}.local",
                            f"{folShape}.inputSurface", f=True)
        cmds.setAttr(f"{folShape}.parameterV", 0.5)
        cmds.setAttr(f"{folShape}.parameterU", param)
        cmds.connectAttr(f"{folShape}.outRotate", f"{fol}.rotate", f=True)
        cmds.connectAttr(f"{folShape}.outTranslate",
                            f"{fol}.translate", f=True)
        '''
        #cmds.error("##")
        # Delete Later
    #     cInfoNodes = []
  
    #     infl = 1 / (self.numberOfJoints - 1)
    #     uPos = 0
    #     indexing = 1
    #     for i in range(self.numberOfJoints):
    #         if uPos > 1.0:
    #             uPos = 1.0
    #         if i == ((self.numberOfJoints - 1)/2)-1:
    #             indexing = 0
    #         if i <= ((self.numberOfJoints-2) / 2):
    #             if i == 0:
    #                 jLabel = f"L_{self.label}_Corner"

    #                 cinfo = cmds.createNode("pointOnCurveInfo", n=f"UpLip_{i}_cInfo")                    
    #                 lCorner = cmds.createNode("joint",
    #                                           n=jLabel)                    
    #                 cmds.connectAttr(f"{upCurve}.worldSpace[0]", f"{cinfo}.inputCurve")
    #                 cmds.connectAttr(f"{cinfo}.result.position", f"{lCorner}.translate")
    #                 cmds.setAttr(f"{cinfo}.parameter", uPos)

    #                 cornerJoints.append(lCorner)
    #                 cInfoNodes.append(cinfo)
    #             # Make Left Joints
    #             else:
    #                 jUpLabel = f"L_{self.label}_Up_{i}"
    #                 jLoLabel = f"L_{self.label}_Lo_{i}"

    #                 nPos = 0.5 - uPos
    #                 upcinfo = cmds.createNode("pointOnCurveInfo", n=f"UpLip_{i}_cInfo")                    
    #                 upJnt = cmds.createNode("joint",
    #                                           n=jUpLabel)
    #                 locinfo = cmds.createNode("pointOnCurveInfo", n=f"LoLip_{i}_cInfo")                    
    #                 loJnt = cmds.createNode("joint",
    #                                           n=jLoLabel)
    #                 cmds.connectAttr(f"{upCurve}.worldSpace[0]", f"{upcinfo}.inputCurve")
    #                 cmds.connectAttr(f"{upcinfo}.result.position", f"{upJnt}.translate")
    #                 cmds.setAttr(f"{upcinfo}.parameter", nPos)
    #                 cmds.connectAttr(f"{loCurve}.worldSpace[0]", f"{locinfo}.inputCurve")
    #                 cmds.connectAttr(f"{locinfo}.result.position", f"{loJnt}.translate")
    #                 cmds.setAttr(f"{locinfo}.parameter", nPos)

    #                 upLipJoints.append(upJnt)
    #                 loLipJoints.append(loJnt)
    #                 cInfoNodes.append(upcinfo)
    #                 cInfoNodes.append(locinfo)
    #                 indexing+=1

    #         elif i >= ((self.numberOfJoints+1) / 2):
    #             if i == self.numberOfJoints - 1:
    #                 jLabel = f"R_{self.label}_Corner"

    #                 cinfo = cmds.createNode("pointOnCurveInfo", n=f"UpLip_{indexing}_cInfo")                    
    #                 rCorner = cmds.createNode("joint",
    #                                           n=jLabel)
                    
    #                 cmds.connectAttr(f"{upCurve}.worldSpace[0]", f"{cinfo}.inputCurve")
    #                 cmds.connectAttr(f"{cinfo}.result.position", f"{rCorner}.translate")
    #                 cmds.setAttr(f"{cinfo}.parameter", uPos)

    #                 cornerJoints.append(rCorner)
    #                 cInfoNodes.append(cinfo)
    #             # Make Right Joints
    #             else:                    
    #                 jUpLabel = f"R_{self.label}_Up_{indexing}"
    #                 jLoLabel = f"R_{self.label}_Lo_{indexing}"

    #                 upcinfo = cmds.createNode("pointOnCurveInfo", n=f"UpLip_{indexing}_cInfo")                    
    #                 upJnt = cmds.createNode("joint",
    #                                           n=jUpLabel)
    #                 locinfo = cmds.createNode("pointOnCurveInfo", n=f"LoLip_{indexing}_cInfo")                    
    #                 loJnt = cmds.createNode("joint",
    #                                           n=jLoLabel)
    #                 cmds.connectAttr(f"{upCurve}.worldSpace[0]", f"{upcinfo}.inputCurve")
    #                 cmds.connectAttr(f"{upcinfo}.result.position", f"{upJnt}.translate")
    #                 cmds.setAttr(f"{upcinfo}.parameter", uPos)
    #                 cmds.connectAttr(f"{loCurve}.worldSpace[0]", f"{locinfo}.inputCurve")
    #                 cmds.connectAttr(f"{locinfo}.result.position", f"{loJnt}.translate")
    #                 cmds.setAttr(f"{locinfo}.parameter", uPos)

    #                 upLipJoints.append(upJnt)
    #                 loLipJoints.append(loJnt)
    #                 cInfoNodes.append(upcinfo)
    #                 cInfoNodes.append(locinfo)
    #                 indexing += 1
    #         else:
    #             # Make Midde Joint
    #             jUpLabel = f"M_{self.label}_Up"
    #             jLoLabel = f"M_{self.label}_Lo"

    #             upcinfo = cmds.createNode("pointOnCurveInfo", n=f"UpLip_{i}_cInfo")                    
    #             upJnt = cmds.createNode("joint",
    #                                         n=jUpLabel)
    #             locinfo = cmds.createNode("pointOnCurveInfo", n=f"LoLip_{i}_cInfo")                    
    #             loJnt = cmds.createNode("joint",
    #                                         n=jLoLabel)
    #             cmds.connectAttr(f"{upCurve}.worldSpace[0]", f"{upcinfo}.inputCurve")
    #             cmds.connectAttr(f"{upcinfo}.result.position", f"{upJnt}.translate")
    #             cmds.setAttr(f"{upcinfo}.parameter", uPos)
    #             cmds.connectAttr(f"{loCurve}.worldSpace[0]", f"{locinfo}.inputCurve")
    #             cmds.connectAttr(f"{locinfo}.result.position", f"{loJnt}.translate")
    #             cmds.setAttr(f"{locinfo}.parameter", uPos)

    #             upLipJoints.append(upJnt)
    #             loLipJoints.append(loJnt)
    #             cInfoNodes.append(upcinfo)
    #             cInfoNodes.append(locinfo)
    #         uPos += infl

    #     # Make position dict
    #     jPos = {}
    #     for u, l in zip(upLipJoints, loLipJoints):
    #         jPos[u] = cmds.xform(u, q=True, ws=True, t=True)
    #         jPos[l] = cmds.xform(l, q=True, ws=True, t=True)
    #     jPos[cornerJoints[0]] = cmds.xform(cornerJoints[0], q=True, ws=True, t=True)
    #     jPos[cornerJoints[1]] = cmds.xform(cornerJoints[1], q=True, ws=True, t=True)
        
    #     cmds.delete(cInfoNodes)
    #     cmds.delete([upCurve, loCurve])
    #     for j, t in jPos.items():
    #         cmds.xform(j, ws=True, t=t)        

    #     # Aim Joints.
    #     lipRange = (len(upLipJoints)-1) / 2

    #     # Order lists
    #     orderedUpLipL = upLipJoints[:int(lipRange):]
    #     orderedUpLipL.insert(0, upLipJoints[int(lipRange)])
    #     orderedLoLipL = loLipJoints[:int(lipRange):]
    #     orderedLoLipL.insert(0, loLipJoints[int(lipRange)])
    #     orderedUpLipR = upLipJoints[int(lipRange)+1::]
    #     orderedLoLipR = loLipJoints[int(lipRange)+1::]

    #     oc = cmds.orientConstraint([upLipJoints[int(lipRange)-1], loLipJoints[int(lipRange)-1]], cornerJoints[0], mo=0)[0]
    #     cmds.setAttr(f"{oc}.interpType", 2)
    #     cmds.delete(oc)
    #     oc = cmds.orientConstraint([upLipJoints[int(lipRange)+1], loLipJoints[int(lipRange)+1]], cornerJoints[1], mo=0)[0]
    #     cmds.setAttr(f"{oc}.interpType", 2)
    #     cmds.delete(oc)
    #     cmds.makeIdentity(upLipJoints, a=True)
    #     cmds.makeIdentity(loLipJoints, a=True)
    #     cmds.makeIdentity(cornerJoints, a=True)     

    #     # components
    #     upParents = []
    #     upZippers = []
    #     upOffsets = []
    #     upCtrls = []
    #     loParents = []
    #     loZippers = []
    #     loOffsets = []
    #     loCtrls = []
    #     cornerParents = []
    #     cornerZippers = []
    #     cornerLocZippers = []
    #     cornerOffsets = []
    #     cornerCtrls = []
    #     upLocZippers = []
    #     loLocZippers = []
    #     upCorrectives = []
    #     loCorrectives = []
    #     cornerCorrectives = []  
    #     upMouthZippers = []
    #     loMouthZippers = []
    #     cornerMouthZippers = []
    #     ptcs = []

    #     # Make control and logic.
    #     for upJnt, loJnt in zip(upLipJoints, loLipJoints):
    #         # Make parent, offset, control
    #         upPar = cmds.createNode("transform", n=f"{upJnt}_grp")
    #         upOffset = cmds.createNode("transform", n=f"{upJnt}_offset", p=upPar)
    #         upCorrective = cmds.createNode("transform", n=f"{upJnt}_corrective", p=upPar)
    #         upZip = cmds.createNode("transform", n=f"{upJnt}_zipper", p=upCorrective)            
    #         upCtrl = cmds.createNode("transform", n=f"{upJnt}_CTRL", p=upZip)
    #         upLocZip = cmds.createNode("transform", n=f"{upJnt}_locator", p=upPar)
    #         upMouthZipper = cmds.createNode("transform", n=f"{upJnt}_mouthTarget", p=upPar)
    #         cmds.xform(upPar, ws=True, m=cmds.xform(upJnt, q=True, ws=True, m=True))
    #         loPar = cmds.createNode("transform", n=f"{loJnt}_grp")
    #         loOffset = cmds.createNode("transform", n=f"{loJnt}_offset", p=loPar)
    #         loCorrective = cmds.createNode("transform", n=f"{loJnt}_corrective", p=loPar)
    #         loZip = cmds.createNode("transform", n=f"{loJnt}_zipper", p=loCorrective)
    #         loCtrl = cmds.createNode("transform", n=f"{loJnt}_CTRL", p=loZip)
    #         loLocZip = cmds.createNode("transform", n=f"{loJnt}_locator", p=loPar)
    #         loMouthZipper = cmds.createNode("transform", n=f"{loJnt}_mouthTarget", p=loPar)
    #         cmds.xform(loPar, ws=True, m=cmds.xform(loJnt, q=True, ws=True, m=True))

    #         ptc_u = cmds.parentConstraint(upCtrl, upJnt, mo=0, n=f"{upJnt}_ptc")[0]
    #         cmds.setAttr(f"{ptc_u}.interpType", 2)
    #         ptc_l = cmds.parentConstraint(loCtrl, loJnt, mo=0, n=f"{loJnt}_ptc")[0]
    #         cmds.setAttr(f"{ptc_l}.interpType", 2)

    #         ptcs.append(ptc_u)
    #         ptcs.append(ptc_l)
    #         up = ctrlCrv.Ctrl(
    #         node=upCtrl,
    #         shape="sphere",
    #         scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.75, self.ctrlScale[2] * 0.75],
    #         offset=[0, 0, 0]
    #         )
    #         up.giveCtrlShape()
    #         lo = ctrlCrv.Ctrl(
    #         node=loCtrl,
    #         shape="sphere",
    #         scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.75, self.ctrlScale[2] * 0.75],
    #         offset=[0, 0, 0]
    #         )
    #         lo.giveCtrlShape()
            
    #         upParents.append(upPar)
    #         upZippers.append(upZip)
    #         upOffsets.append(upOffset)
    #         upCtrls.append(upCtrl)
    #         upLocZippers.append(upLocZip)
    #         upCorrectives.append(upCorrective)
    #         upMouthZippers.append(upMouthZipper)
            
    #         loParents.append(loPar)
    #         loZippers.append(loZip)
    #         loOffsets.append(loOffset)
    #         loCtrls.append(loCtrl)
    #         loLocZippers.append(loLocZip)
    #         loCorrectives.append(loCorrective)
    #         loMouthZippers.append(loMouthZipper)

    #     for corner in cornerJoints:
    #         par = cmds.createNode("transform", n=f"{corner}_grp")
    #         offset = cmds.createNode("transform", n=f"{corner}_offset", p=par)
    #         corrective = cmds.createNode("transform", n=f"{corner}_corrective", p=par)
    #         czip = cmds.createNode("transform", n=f"{corner}_zipper", p=offset)
    #         ctrl = cmds.createNode("transform", n=f"{corner}_CTRL", p=offset)
    #         cLocZip = cmds.createNode("transform", n=f"{corner}_locator", p=par)
    #         cMouthZipper = cmds.createNode("transform", n=f"{corner}_mouthTarget", p=par)
    #         cmds.xform(par, ws=True, m=cmds.xform(corner, q=True, ws=True, m=True))
    #         ptc = cmds.parentConstraint(ctrl, corner, mo=0, n=f"{corner}_ptc")[0]
    #         cmds.setAttr(f"{ptc}.interpType", 2)
    #         ptcs.append(ptc)

    #         cornerParents.append(par)
    #         cornerZippers.append(czip)
    #         cornerOffsets.append(offset)
    #         cornerCtrls.append(ctrl)
    #         cornerLocZippers.append(cLocZip)
    #         cornerCorrectives.append(corrective)
    #         cornerMouthZippers.append(cMouthZipper)
    #         crnr = ctrlCrv.Ctrl(
    #         node=ctrl,
    #         shape="sphere",
    #         scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.75, self.ctrlScale[2] * 0.75],
    #         offset=[0, 0, 0]
    #         )
    #         crnr.giveCtrlShape()
    #     for up, lp in zip(upParents[int(lipRange+1)::], loParents[int(lipRange+1)::]):
    #         cmds.setAttr(f"{up}.scaleX", -1)
    #         cmds.setAttr(f"{lp}.scaleX", -1)
    #     cmds.setAttr(f"{cornerParents[1]}.scaleX", -1)

    #     # Side Inversion
    #     lGroup = cmds.createNode("transform", n=f"L_{self.label}_controls")
    #     rGroup = cmds.createNode("transform", n=f"R_{self.label}_controls")

    #     cmds.parent(upParents[:int(lipRange):], lGroup)
    #     cmds.parent(loParents[:int(lipRange):], lGroup)
    #     cmds.parent(cornerParents[0], lGroup)
    #     cmds.setAttr(f"{rGroup}.scaleX", -1)
    #     cmds.parent(upParents[int(lipRange+1)::], rGroup)
    #     cmds.parent(loParents[int(lipRange+1)::], rGroup)
    #     cmds.parent(cornerParents[1], rGroup)

    #     # Make constraints
    #     upMiddlePar = cmds.createNode("transform", n=f"{upLipJoints[int(lipRange)]}_Main_grp")
    #     upMiddleCtrl = cmds.createNode("transform", n=f"{upLipJoints[int(lipRange)]}_Main_CTRL", p=upMiddlePar)
    #     loMiddlePar = cmds.createNode("transform", n=f"{loLipJoints[int(lipRange)]}_Main_grp")
    #     loMiddleCtrl = cmds.createNode("transform", n=f"{loLipJoints[int(lipRange)]}_Main_CTRL", p=loMiddlePar)
    #     lCornerPar = cmds.createNode("transform", n=f"{cornerJoints[0]}_Main_grp")
    #     lCornerCtrl = cmds.createNode("transform", n=f"{cornerJoints[0]}_Main_CTRL", p=lCornerPar)
    #     rCornerPar = cmds.createNode("transform", n=f"{cornerJoints[1]}_Main_grp")
    #     rCornerCtrl = cmds.createNode("transform", n=f"{cornerJoints[1]}_Main_CTRL", p=rCornerPar)
    #     um = ctrlCrv.Ctrl(
    #         node=upMiddleCtrl,
    #         shape="sphere",
    #         scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
    #         offset=[0, 0, 0]
    #         )
    #     um.giveCtrlShape()
    #     lm = ctrlCrv.Ctrl(
    #         node=loMiddleCtrl,
    #         shape="sphere",
    #         scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
    #         offset=[0, 0, 0]
    #         )
    #     lm.giveCtrlShape()
    #     lc = ctrlCrv.Ctrl(
    #         node=lCornerCtrl,
    #         shape="sphere",
    #         scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
    #         offset=[0, 0, 0]
    #         )
    #     lc.giveCtrlShape()
    #     rc = ctrlCrv.Ctrl(
    #         node=rCornerCtrl,
    #         shape="sphere",
    #         scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
    #         offset=[0, 0, 0]
    #         )
    #     rc.giveCtrlShape()

    #     cmds.xform(upMiddlePar, ws=True, t=cmds.xform(upLipJoints[int(lipRange)], q=True, ws=True, t=True))
    #     cmds.xform(loMiddlePar, ws=True, t=cmds.xform(loLipJoints[int(lipRange)], q=True, ws=True, t=True))
    #     cmds.xform(lCornerPar, ws=True, t=cmds.xform(cornerJoints[0], q=True, ws=True, t=True))
    #     cmds.xform(rCornerPar, ws=True, t=cmds.xform(cornerJoints[1], q=True, ws=True, t=True))
    #     cmds.setAttr(f"{rCornerPar}.scaleX", -1)

    #     cmds.parent(lCornerPar, lGroup)
    #     cmds.parent(rCornerPar, rGroup)

    #     ptc = cmds.parentConstraint(upMiddleCtrl, upOffsets[int(lipRange)], mo=1, n=f"{upParents[int(lipRange)]}_ptc")
    #     ptc = cmds.parentConstraint(loMiddleCtrl, loOffsets[int(lipRange)], mo=1, n=f"{loParents[int(lipRange)]}_ptc")
    #     ptc = cmds.parentConstraint(lCornerCtrl, cornerParents[0], mo=1, n=f"{cornerParents[0]}_ptc")
    #     ptc = cmds.parentConstraint(rCornerCtrl, cornerParents[1], mo=1, n=f"{cornerParents[1]}_ptc")

    #     # Oh for fucks sake. Ok, make list starting with M control, reverse list for R side. 
    #     upLOffsets = upOffsets[:int(lipRange):]
    #     upLOffsets.insert(0, upOffsets[int(lipRange)])
    #     loLOffsets = loOffsets[:int(lipRange):]
    #     loLOffsets.insert(0, loOffsets[int(lipRange)])
    #     upROffsets = upOffsets[int(lipRange)+1::]
    #     upROffsets.insert(0, upOffsets[int(lipRange)])
    #     loROffsets = loOffsets[int(lipRange)+1::]
    #     loROffsets.insert(0, loOffsets[int(lipRange)])
    #     acs = []
    #     for i in range(len(upLOffsets)-1):
    #         ac_ul = cmds.aimConstraint(upLOffsets[i], upLOffsets[i+1], mo=0, 
    #                                 n=f"{upLOffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
    #                                 u=jointTools.axisToVector(self.upAxis), wuo=upLOffsets[i], wut="object")[0]
    #         ac_ll = cmds.aimConstraint(loLOffsets[i], loLOffsets[i+1], mo=0, 
    #                                 n=f"{loLOffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
    #                                 u=jointTools.axisToVector(self.upAxis), wuo=loLOffsets[i], wut="object")[0]
    #         ac_ur = cmds.aimConstraint(upROffsets[i], upROffsets[i+1], mo=0, 
    #                                 n=f"{upROffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
    #                                 u=jointTools.axisToVector(jointTools.axisFlip(self.upAxis)), wuo=upROffsets[i], wut="object")[0]
    #         ac_lr = cmds.aimConstraint(loROffsets[i], loROffsets[i+1], mo=0 , 
    #                                 n=f"{loROffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
    #                                 u=jointTools.axisToVector(jointTools.axisFlip(self.upAxis)), wuo=loROffsets[i], wut="object")[0]
    #         acs.extend([ac_ul, ac_ll, ac_ur, ac_lr])
    #     cmds.delete(acs)
    #     cmds.delete(ptcs)
    #     cmds.makeIdentity(upLipJoints, a=True)
    #     cmds.makeIdentity(loLipJoints, a=True)
    #     cmds.makeIdentity(cornerJoints, a=True)
        
    #     for i in range(len(upLipJoints)):# zip(upLipJoints, loLipJoints):
    #         ptc = cmds.parentConstraint(upCtrls[i], upLipJoints[i], mo=0, n=f"{upLipJoints[i]}_ptc")[0]
    #         cmds.setAttr(f"{ptc}.interpType", 2)
    #         ptc = cmds.parentConstraint(loCtrls[i], loLipJoints[i], mo=0, n=f"{loLipJoints[i]}_ptc")[0]
    #         cmds.setAttr(f"{ptc}.interpType", 2)
    #     for i in range(2):
    #         ptc = cmds.parentConstraint(cornerCtrls[i], cornerJoints[i], n=f"{cornerJoints[i]}_ptc", mo=0)
    #     for i in range(len(upLOffsets)-1):
    #         ac_ul = cmds.aimConstraint(upLOffsets[i], upLOffsets[i+1], mo=0, 
    #                                 n=f"{upLOffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
    #                                 u=jointTools.axisToVector(self.upAxis), wuo=upLOffsets[i], wut="object",
    #                                 sk="x")[0]
    #         ac_ll = cmds.aimConstraint(loLOffsets[i], loLOffsets[i+1], mo=0, 
    #                                 n=f"{loLOffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
    #                                 u=jointTools.axisToVector(self.upAxis), wuo=loLOffsets[i], wut="object",
    #                                 sk="x")[0]
    #         ac_ur = cmds.aimConstraint(upROffsets[i], upROffsets[i+1], mo=0, 
    #                                 n=f"{upROffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
    #                                 u=jointTools.axisToVector(jointTools.axisFlip(self.upAxis)), wuo=upROffsets[i], wut="object",
    #                                 sk="x")[0]
    #         ac_lr = cmds.aimConstraint(loROffsets[i], loROffsets[i+1], mo=0 , 
    #                                 n=f"{loROffsets[i+1]}_ac", aim=jointTools.axisToVector(jointTools.axisFlip(self.aimAxis)),
    #                                 u=jointTools.axisToVector(jointTools.axisFlip(self.upAxis)), wuo=loROffsets[i], wut="object",
    #                                 sk="x")[0]
        

    #     inflCalc = 0.0
    #     inflVal = 1 / (lipRange+1)
        

    #     for i in range(int(lipRange)):
    #         inflCalc +=inflVal
    #         # Make lip MD / PMA
    #         mlUpMd = cmds.createNode("multiplyDivide", n=f"{upLipJoints[:int(lipRange):][i]}_M_MD")
    #         lUpMd = cmds.createNode("multiplyDivide", n=f"{upLipJoints[:int(lipRange):][i]}_L_MD")
    #         lUpPma = cmds.createNode("plusMinusAverage", n=f"{upLipJoints[:int(lipRange):][i]}_PMA")
    #         mlLoMd = cmds.createNode("multiplyDivide", n=f"{loLipJoints[:int(lipRange):][i]}_M_MD")
    #         lLoMd = cmds.createNode("multiplyDivide", n=f"{loLipJoints[:int(lipRange):][i]}_L_MD")
    #         lLoPma = cmds.createNode("plusMinusAverage", n=f"{upLipJoints[:int(lipRange):][i]}_PMA")
    #         mrUpMd = cmds.createNode("multiplyDivide", n=f"{upLipJoints[:int(lipRange):-1][i]}_M_MD")
    #         rUpMd = cmds.createNode("multiplyDivide", n=f"{upLipJoints[:int(lipRange):-1][i]}_R_MD")
    #         rUpPma = cmds.createNode("plusMinusAverage", n=f"{upLipJoints[:int(lipRange):-1][i]}_PMA")
    #         mrLoMd = cmds.createNode("multiplyDivide", n=f"{loLipJoints[:int(lipRange):-1][i]}_M_MD")
    #         rLoMd = cmds.createNode("multiplyDivide", n=f"{loLipJoints[:int(lipRange):-1][i]}_R_MD")
    #         rLoPma = cmds.createNode("plusMinusAverage", n=f"{upLipJoints[:int(lipRange):-1][i]}_PMA")
            
    #         # Connect Attributes
    #         # Up Left Attr Connections
    #         cmds.connectAttr(f"{upMiddleCtrl}.translate", f"{mlUpMd}.input1")
    #         cmds.connectAttr(f"{lCornerCtrl}.translate", f"{lUpMd}.input1")
    #         cmds.connectAttr(f"{mlUpMd}.output", f"{lUpPma}.input3D[0]")
    #         cmds.connectAttr(f"{lUpMd}.output", f"{lUpPma}.input3D[1]")
    #         cmds.connectAttr(f"{lUpPma}.output3D", f"{upOffsets[:int(lipRange):][i]}.translate")
    #         # Lo Left Attr Connections
    #         cmds.connectAttr(f"{loMiddleCtrl}.translate", f"{mlLoMd}.input1")
    #         cmds.connectAttr(f"{lCornerCtrl}.translate", f"{lLoMd}.input1")
    #         cmds.connectAttr(f"{mlLoMd}.output", f"{lLoPma}.input3D[0]")
    #         cmds.connectAttr(f"{lLoMd}.output", f"{lLoPma}.input3D[1]")
    #         cmds.connectAttr(f"{lLoPma}.output3D", f"{loOffsets[:int(lipRange):][i]}.translate")
    #         # Up Right Attr Connections
    #         cmds.connectAttr(f"{upMiddleCtrl}.translate", f"{mrUpMd}.input1")
    #         cmds.connectAttr(f"{rCornerCtrl}.translate", f"{rUpMd}.input1")
    #         cmds.connectAttr(f"{mrUpMd}.output", f"{rUpPma}.input3D[0]")
    #         cmds.connectAttr(f"{rUpMd}.output", f"{rUpPma}.input3D[1]")
    #         cmds.connectAttr(f"{rUpPma}.output3D", f"{upOffsets[int(lipRange)+1::][i]}.translate")
    #         # Lo Right Attr Connections
    #         cmds.connectAttr(f"{loMiddleCtrl}.translate", f"{mrLoMd}.input1")
    #         cmds.connectAttr(f"{rCornerCtrl}.translate", f"{rLoMd}.input1")
    #         cmds.connectAttr(f"{mrLoMd}.output", f"{rLoPma}.input3D[0]")
    #         cmds.connectAttr(f"{rLoMd}.output", f"{rLoPma}.input3D[1]")
    #         cmds.connectAttr(f"{rLoPma}.output3D", f"{loOffsets[int(lipRange)+1::][i]}.translate")

    #         # Set Calc Values
    #         sine = self.easeInCubic(input=inflCalc)
    #         # cubicIn = self.easeInCubic(input=inflCalc)
    #         # sineIn = self.easeInSine(input=inflCalc)
    #         cubicIn = self.easeInSine(input=inflCalc)
    #         sineIn = inflCalc

    #         # Up Left
    #         cmds.setAttr(f"{mlUpMd}.input2.input2X", 1.0-sineIn)
    #         cmds.setAttr(f"{mlUpMd}.input2.input2Y", (1.0-cubicIn))
    #         cmds.setAttr(f"{mlUpMd}.input2.input2Z", (1.0-cubicIn))
    #         cmds.setAttr(f"{lUpMd}.input2.input2X", sineIn)
    #         cmds.setAttr(f"{lUpMd}.input2.input2Y", (cubicIn))
    #         cmds.setAttr(f"{lUpMd}.input2.input2Z", (cubicIn))
    #         # Lo Left
    #         cmds.setAttr(f"{mlLoMd}.input2.input2X", 1.0-sineIn)
    #         cmds.setAttr(f"{mlLoMd}.input2.input2Y", (1.0-cubicIn))
    #         cmds.setAttr(f"{mlLoMd}.input2.input2Z", (1.0-cubicIn))
    #         cmds.setAttr(f"{lLoMd}.input2.input2X", sineIn)
    #         cmds.setAttr(f"{lLoMd}.input2.input2Y", (cubicIn))
    #         cmds.setAttr(f"{lLoMd}.input2.input2Z", (cubicIn))
    #         # Up Right
    #         cmds.setAttr(f"{mrUpMd}.input2.input2X", (1.0-sineIn)*-1)
    #         cmds.setAttr(f"{mrUpMd}.input2.input2Y", (1.0-cubicIn))
    #         cmds.setAttr(f"{mrUpMd}.input2.input2Z", 1.0-cubicIn)
    #         cmds.setAttr(f"{rUpMd}.input2.input2X", (sineIn))
    #         cmds.setAttr(f"{rUpMd}.input2.input2Y", (cubicIn))
    #         cmds.setAttr(f"{rUpMd}.input2.input2Z", cubicIn)
    #         # Lo Right
    #         cmds.setAttr(f"{mrLoMd}.input2.input2X", (1.0-sineIn)*-1)
    #         cmds.setAttr(f"{mrLoMd}.input2.input2Y", (1.0-cubicIn))
    #         cmds.setAttr(f"{mrLoMd}.input2.input2Z", 1.0-cubicIn)
    #         cmds.setAttr(f"{rLoMd}.input2.input2X", (sineIn))
    #         cmds.setAttr(f"{rLoMd}.input2.input2Y", (cubicIn))
    #         cmds.setAttr(f"{rLoMd}.input2.input2Z", cubicIn)
        
    #     for i, j in zip(upOffsets, loOffsets):
    #         if i != upOffsets[int(lipRange)]:
    #             cmds.connectAttr(f"{upMiddleCtrl}.rotateX", f"{i}.rotateX")
    #         if j != loOffsets[int(lipRange)]:
    #             cmds.connectAttr(f"{loMiddleCtrl}.rotateX", f"{j}.rotateX")

    #     oc = cmds.orientConstraint([upOffsets[int(lipRange-1)], loOffsets[int(lipRange-1)]], cornerOffsets[0],
    #                                n=f"{cornerOffsets[0]}_oc", mo=1)[0]
    #     cmds.setAttr(f"{oc}.interpType", 2)
    #     oc = cmds.orientConstraint([upOffsets[-1], loOffsets[-1]], cornerOffsets[1],
    #                                n=f"{cornerOffsets[1]}_oc", mo=1)[0]
    #     cmds.setAttr(f"{oc}.interpType", 2)

    #     '''
    #     Ight, next up. Mouth controls, fuck me.

    #     3 Control (plus optional jaw influence if added as a var)
    #     UpMouth/LoMouth: Ctrl drives a transform, child of transform is joint. Blends between the 
    #             Up/LoMouth ctrl at the same CubicIn val as the UpLip_Main/LoLip_Main controls
    #             as well as 50/50 blending the Corner_Main controls. Joint ptc 50/50 the Mouth parent
    #     Mouth: ctrl directly drives the t/r/s of the UpMouth/LoMouth joint. 
    #     If there is a jaw, Mouth and loMouth become children PTC of jaw
    #     '''

    #     mouthPar = cmds.createNode("transform", n=f"{self.side}_{self.label}_Mouth_grp")
    #     mouthOffset = cmds.createNode("transform", n=f"{self.side}_{self.label}_Mouth_offset", p=mouthPar)
    #     mouthCtrl = cmds.createNode("transform", n=f"{self.side}_{self.label}_Mouth_CTRL", p=mouthOffset)
    #     # mouthJoint = cmds.createNode("joint", n=f"{self.side}_{self.label}_Mouth", p=mouthCtrl)
    #     mouth = ctrlCrv.Ctrl(
    #         node=mouthCtrl,
    #         shape="box",
    #         scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.75, self.ctrlScale[2] * 0.75],
    #         offset=[0, 0, self.ctrlScale[2] * 1.5]
    #         )
    #     mouth.giveCtrlShape()

    #     upMouthPar = cmds.createNode("transform", n=f"{self.side}_{self.label}_UpMouth_grp")
    #     upMouthOffset = cmds.createNode("transform", n=f"{self.side}_{self.label}_UpMouth_offset", p=upMouthPar)
    #     upMouthCtrl = cmds.createNode("transform", n=f"{self.side}_{self.label}_UpMouth_CTRL", p=upMouthOffset)
    #     # upMouthJoint = cmds.createNode("joint", n=f"{self.side}_{self.label}_UpMouth", p=upMouthCtrl)
    #     upMouth = ctrlCrv.Ctrl(
    #         node=upMouthCtrl,
    #         shape="circle",
    #         scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.25, self.ctrlScale[2] * 0.75],
    #         offset=[0, self.ctrlScale[1], self.ctrlScale[2] * 1.5]
    #         )
    #     upMouth.giveCtrlShape()

    #     loMouthPar = cmds.createNode("transform", n=f"{self.side}_{self.label}_LoMouth_grp")
    #     loMouthOffset = cmds.createNode("transform", n=f"{self.side}_{self.label}_LoMouth_offset", p=loMouthPar)
    #     loMouthCtrl = cmds.createNode("transform", n=f"{self.side}_{self.label}_LoMouth_CTRL", p=loMouthOffset)
    #     # loMouthJoint = cmds.createNode("joint", n=f"{self.side}_{self.label}_LoMouth", p=loMouthCtrl)
    #     loMouth = ctrlCrv.Ctrl(
    #         node=loMouthCtrl,
    #         shape="circle",
    #         scale=[self.ctrlScale[0] * 0.75, self.ctrlScale[1] * 0.25, self.ctrlScale[2] * 0.75],
    #         offset=[0, self.ctrlScale[1] * -1, self.ctrlScale[2] * 1.5]
    #         )
    #     loMouth.giveCtrlShape()

    #     cmds.xform(mouthPar, ws=True, t=cmds.xform(
    #         f"{self.side}_{self.label}_{self.proxies['Mouth'].name}_proxy",
    #         q=True, t=True
    #     ))
    #     cmds.xform(upMouthPar, ws=True, t=cmds.xform(
    #         f"{self.side}_{self.label}_{self.proxies['Mouth'].name}_proxy",
    #         q=True, t=True
    #     ))
    #     cmds.xform(loMouthPar, ws=True, t=cmds.xform(
    #         f"{self.side}_{self.label}_{self.proxies['Mouth'].name}_proxy",
    #         q=True, t=True
    #     ))

    #     cmds.addAttr(mouthCtrl, ln="zipper", at="float", min=0.0, max=2.0, dv=1.0, k=True)

    #     # Ok some fucking madness here I'll document later.... fuck me
    #     inflCalc = 0.0
    #     inflVal = 1 / (lipRange+1)
    #     rangeValues = []
    #     for i in range(int(lipRange)):
    #         inflCalc += inflVal
    #         sineIn = self.easeInSine(input=inflCalc)
    #         cubicIn = self.easeInCubic(input=inflCalc)
    #         circIn = self.easeInCirc(input=inflCalc)
    #         rangeValues.append(circIn)

    #     index = -1

    #     cmds.parent(upMouthZippers, mouthCtrl)
    #     cmds.parent(loMouthZippers, mouthCtrl)
    #     cmds.parent(cornerMouthZippers, mouthCtrl)

    #     for i in range((int(lipRange))):
    #         #pass
    #         ptc = cmds.parentConstraint([upMouthCtrl, loMouthCtrl, upMouthZippers[:int(lipRange):][i]], 
    #                                     upParents[:int(lipRange):][i],
    #                                     n=f"{upParents[:int(lipRange):][i]}_BC", mo=1)[0]
            
    #         bc = cmds.createNode("blendColors", n=f"{upParents[:int(lipRange):][i]}_BC")

    #         cmds.setAttr(f"{bc}.color1R", 1.0-rangeValues[i])
    #         cmds.setAttr(f"{bc}.color1G", rangeValues[i])
    #         cmds.setAttr(f"{bc}.color1B", 0.0)
    #         cmds.setAttr(f"{bc}.color2R", 0.0)
    #         cmds.setAttr(f"{bc}.color2G", 0.0)
    #         cmds.setAttr(f"{bc}.color2B", 1.0)

    #         cmds.connectAttr(f"{mouthCtrl}.zipper", f"{bc}.blender")

    #         cmds.setAttr(f"{ptc}.interpType", 2)

    #         # cmds.setAttr(f"{ptc}.{upMouthCtrl}W0", 1.0-rangeValues[i])
    #         # cmds.setAttr(f"{ptc}.{loMouthCtrl}W1", rangeValues[i])

    #         cmds.connectAttr(f"{bc}.outputR", f"{ptc}.{upMouthCtrl}W0")
    #         cmds.connectAttr(f"{bc}.outputG", f"{ptc}.{loMouthCtrl}W1")
    #         cmds.connectAttr(f"{bc}.outputB", f"{ptc}.{upMouthZippers[:int(lipRange):][i]}W2")

    #         ptc = cmds.parentConstraint([upMouthCtrl, loMouthCtrl, upMouthZippers[:int(lipRange):-1][i]], 
    #                                     upParents[:int(lipRange):-1][i],
    #                                     n=f"{upParents[:int(lipRange):-1][i]}_ptc", mo=1)[0]
            
    #         bc = cmds.createNode("blendColors", n=f"{upParents[:int(lipRange):-1][i]}_BC")

    #         cmds.setAttr(f"{bc}.color1R", 1.0-rangeValues[index])
    #         cmds.setAttr(f"{bc}.color1G", rangeValues[index])
    #         cmds.setAttr(f"{bc}.color1B", 0.0)
    #         cmds.setAttr(f"{bc}.color2R", 0.0)
    #         cmds.setAttr(f"{bc}.color2G", 0.0)
    #         cmds.setAttr(f"{bc}.color2B", 1.0)

    #         cmds.connectAttr(f"{mouthCtrl}.zipper", f"{bc}.blender")

    #         cmds.setAttr(f"{ptc}.interpType", 2)

    #         # cmds.setAttr(f"{ptc}.{upMouthCtrl}W0", 1.0-rangeValues[index])
    #         # cmds.setAttr(f"{ptc}.{loMouthCtrl}W1", rangeValues[index])

    #         cmds.connectAttr(f"{bc}.outputR", f"{ptc}.{upMouthCtrl}W0")
    #         cmds.connectAttr(f"{bc}.outputG", f"{ptc}.{loMouthCtrl}W1")
    #         cmds.connectAttr(f"{bc}.outputB", f"{ptc}.{upMouthZippers[:int(lipRange):-1][i]}W2")

    #         ptc = cmds.parentConstraint([upMouthCtrl, loMouthCtrl, loMouthZippers[:int(lipRange):][i]], 
    #                                     loParents[:int(lipRange):][i],
    #                                     n=f"{loParents[:int(lipRange):][i]}_ptc", mo=1)[0]
            
    #         bc = cmds.createNode("blendColors", n=f"{loParents[:int(lipRange):][i]}_BC")

    #         cmds.setAttr(f"{bc}.color1R", rangeValues[i])
    #         cmds.setAttr(f"{bc}.color1G", 1.0-rangeValues[i])
    #         cmds.setAttr(f"{bc}.color1B", 0.0)
    #         cmds.setAttr(f"{bc}.color2R", 0.0)
    #         cmds.setAttr(f"{bc}.color2G", 0.0)
    #         cmds.setAttr(f"{bc}.color2B", 1.0)

    #         cmds.connectAttr(f"{mouthCtrl}.zipper", f"{bc}.blender")

    #         cmds.setAttr(f"{ptc}.interpType", 2)

    #         # cmds.setAttr(f"{ptc}.{upMouthCtrl}W0", rangeValues[i])
    #         # cmds.setAttr(f"{ptc}.{loMouthCtrl}W1", 1.0-rangeValues[i])

    #         cmds.connectAttr(f"{bc}.outputR", f"{ptc}.{upMouthCtrl}W0")
    #         cmds.connectAttr(f"{bc}.outputG", f"{ptc}.{loMouthCtrl}W1")
    #         cmds.connectAttr(f"{bc}.outputB", f"{ptc}.{loMouthZippers[:int(lipRange):][i]}W2")

    #         ptc = cmds.parentConstraint([upMouthCtrl, loMouthCtrl, loMouthZippers[:int(lipRange):-1][i]], 
    #                                     loParents[:int(lipRange):-1][i],
    #                                     n=f"{loParents[:int(lipRange):-1][i]}_ptc", mo=1)[0]
            
    #         bc = cmds.createNode("blendColors", n=f"{loParents[:int(lipRange):-1][i]}_BC")

    #         cmds.setAttr(f"{bc}.color1R", rangeValues[index])
    #         cmds.setAttr(f"{bc}.color1G", 1.0-rangeValues[index])
    #         cmds.setAttr(f"{bc}.color1B", 0.0)
    #         cmds.setAttr(f"{bc}.color2R", 0.0)
    #         cmds.setAttr(f"{bc}.color2G", 0.0)
    #         cmds.setAttr(f"{bc}.color2B", 1.0)

    #         cmds.connectAttr(f"{mouthCtrl}.zipper", f"{bc}.blender")

    #         cmds.setAttr(f"{ptc}.interpType", 2)

    #         # cmds.setAttr(f"{ptc}.{upMouthCtrl}W0", rangeValues[index])
    #         # cmds.setAttr(f"{ptc}.{loMouthCtrl}W1", 1.0-rangeValues[index])

    #         cmds.connectAttr(f"{bc}.outputR", f"{ptc}.{upMouthCtrl}W0")
    #         cmds.connectAttr(f"{bc}.outputG", f"{ptc}.{loMouthCtrl}W1")
    #         cmds.connectAttr(f"{bc}.outputB", f"{ptc}.{loMouthZippers[:int(lipRange):-1][i]}W2")

    #         index-=1

    #     ptc = cmds.parentConstraint([upMouthCtrl, loMouthCtrl, upMouthZippers[int(lipRange)]], 
    #                                 upParents[int(lipRange)],
    #                                 n=f"{upParents[int(lipRange)]}_ptc", mo=1)[0]
        
    #     bc = cmds.createNode("blendColors", n=f"{upParents[int(lipRange)]}_BC")

    #     cmds.setAttr(f"{bc}.color1R", 1.0)
    #     cmds.setAttr(f"{bc}.color1G", 0.0)
    #     cmds.setAttr(f"{bc}.color1B", 0.0)
    #     cmds.setAttr(f"{bc}.color2R", 0.0)
    #     cmds.setAttr(f"{bc}.color2G", 0.0)
    #     cmds.setAttr(f"{bc}.color2B", 1.0)

    #     cmds.connectAttr(f"{mouthCtrl}.zipper", f"{bc}.blender")

    #     cmds.setAttr(f"{ptc}.interpType", 2)

    #     # cmds.setAttr(f"{ptc}.{upMouthCtrl}W0", 1)
    #     # cmds.setAttr(f"{ptc}.{loMouthCtrl}W1", 0)

    #     cmds.connectAttr(f"{bc}.outputR", f"{ptc}.{upMouthCtrl}W0")
    #     cmds.connectAttr(f"{bc}.outputG", f"{ptc}.{loMouthCtrl}W1")
    #     cmds.connectAttr(f"{bc}.outputB", f"{ptc}.{upMouthZippers[int(lipRange)]}W2")

    #     ptc = cmds.parentConstraint([upMouthCtrl, loMouthCtrl], upMiddlePar,
    #                                     n=f"{upMiddlePar}_ptc", mo=1)[0]
    
    #     cmds.setAttr(f"{ptc}.interpType", 2)

    #     cmds.setAttr(f"{ptc}.{upMouthCtrl}W0", 1)
    #     cmds.setAttr(f"{ptc}.{loMouthCtrl}W1", 0)

    #     ptc = cmds.parentConstraint([upMouthCtrl, loMouthCtrl, loMouthZippers[int(lipRange)]], loParents[int(lipRange)],
    #                                     n=f"{loParents[int(lipRange)]}_ptc", mo=1)[0]
        
    #     bc = cmds.createNode("blendColors", n=f"{loMouthZippers[int(lipRange)]}_BC")

    #     cmds.setAttr(f"{bc}.color1R", 0.0)
    #     cmds.setAttr(f"{bc}.color1G", 1.0)
    #     cmds.setAttr(f"{bc}.color1B", 0.0)
    #     cmds.setAttr(f"{bc}.color2R", 0.0)
    #     cmds.setAttr(f"{bc}.color2G", 0.0)
    #     cmds.setAttr(f"{bc}.color2B", 1.0)

    #     cmds.connectAttr(f"{mouthCtrl}.zipper", f"{bc}.blender")

    #     cmds.setAttr(f"{ptc}.interpType", 2)

    #     # cmds.setAttr(f"{ptc}.{upMouthCtrl}W0", 0)
    #     # cmds.setAttr(f"{ptc}.{loMouthCtrl}W1", 1)

    #     cmds.connectAttr(f"{bc}.outputR", f"{ptc}.{upMouthCtrl}W0")
    #     cmds.connectAttr(f"{bc}.outputG", f"{ptc}.{loMouthCtrl}W1")
    #     cmds.connectAttr(f"{bc}.outputB", f"{ptc}.{loMouthZippers[int(lipRange)]}W2")

    #     ptc = cmds.parentConstraint([upMouthCtrl, loMouthCtrl], loMiddlePar,
    #                                     n=f"{upMiddlePar}_ptc", mo=1)[0]
        
    #     cmds.setAttr(f"{ptc}.interpType", 2)

    #     cmds.setAttr(f"{ptc}.{upMouthCtrl}W0", 0)
    #     cmds.setAttr(f"{ptc}.{loMouthCtrl}W1", 1)
    #     index = 0
    #     for i in [lCornerPar, rCornerPar]:
    #         ptc = cmds.parentConstraint([upMouthCtrl, loMouthCtrl, cornerMouthZippers[index]], i,
    #                                         n=f"{i}_ptc", mo=1)[0]
            
    #         bc = cmds.createNode("blendColors", n=f"{loMouthZippers[int(lipRange)]}_BC")

    #         cmds.setAttr(f"{bc}.color1R", 0.5)
    #         cmds.setAttr(f"{bc}.color1G", 0.5)
    #         cmds.setAttr(f"{bc}.color1B", 0.0)
    #         cmds.setAttr(f"{bc}.color2R", 0.0)
    #         cmds.setAttr(f"{bc}.color2G", 0.0)
    #         cmds.setAttr(f"{bc}.color2B", 1.0)

    #         cmds.connectAttr(f"{mouthCtrl}.zipper", f"{bc}.blender")

    #         cmds.setAttr(f"{ptc}.interpType", 2)

    #         # cmds.setAttr(f"{ptc}.{upMouthCtrl}W0", 0.5)
    #         # cmds.setAttr(f"{ptc}.{loMouthCtrl}W1", 0.5)

    #         cmds.connectAttr(f"{bc}.outputR", f"{ptc}.{upMouthCtrl}W0")
    #         cmds.connectAttr(f"{bc}.outputG", f"{ptc}.{loMouthCtrl}W1")
    #         cmds.connectAttr(f"{bc}.outputB", f"{ptc}.{cornerMouthZippers[index]}W2")

    #     index+=1

    #     if self.jawTarget:
    #         if self.jawTarget is not None:
    #             if cmds.objExists(self.jawTarget):
    #                 ptc = cmds.parentConstraint(self.jawTarget, loMouthPar, 
    #                                             n=f"{loMouthPar}_jawTarget_ptc", mo=1)[0]
    #                 ptc = cmds.parentConstraint(self.jawTarget, mouthPar, 
    #                                             n=f"{mouthPar}_jawTarget_ptc", mo=1)[0]
    #     for i in [upMouthOffset, loMouthOffset]:
    #         cmds.connectAttr(f"{mouthCtrl}.translate", f"{i}.translate")
    #         cmds.connectAttr(f"{mouthCtrl}.rotate", f"{i}.rotate")
    #         cmds.connectAttr(f"{mouthCtrl}.scale", f"{i}.scale")

    #     ptc = cmds.parentConstraint([upMouthPar, loMouthPar], mouthOffset,
    #                                 n=f"{mouthOffset}_blend_ptc", mo=1)[0]
    #     cmds.setAttr(f"{ptc}.interpType", 2)

    #     index = 0
    #     for i in upOffsets:
    #         cmds.xform(upLocZippers[index], ws=True, ro=cmds.xform(i, q=True, ws=True, ro=True))
    #         cmds.xform(loLocZippers[index], ws=True, ro=cmds.xform(loOffsets[index], q=True, ws=True, ro=True))
    #         cmds.xform(upCorrectives[index], ws=True, ro=cmds.xform(i, q=True, ws=True, ro=True))
    #         cmds.xform(loCorrectives[index], ws=True, ro=cmds.xform(loOffsets[index], q=True, ws=True, ro=True))
    #         index+=1

    #     index = 0
    #     for i in cornerOffsets:
    #         cmds.xform(cornerLocZippers[index], ws=True, ro=cmds.xform(i, q=True, ws=True, ro=True))
    #         cmds.xform(cornerCorrectives[index], ws=True, ro=cmds.xform(i, q=True, ws=True, ro=True))
    #         index+=1

    #     lipRange = int(len(upLipJoints)-1)
    #     rangeSet = int(lipRange/2)

    #     rangeSetInfl = 1 / (rangeSet+1)

    #     rangeCatch = 0
    #     index = 0
    #     rangeCatch+=rangeSetInfl
    #     for up, lo in zip(upLipJoints, loLipJoints):
    #         upMM = cmds.createNode("multMatrix", n=f"{up}_zipper_MM")
    #         loMM = cmds.createNode("multMatrix", n=f"{lo}_zipper_MM")
    #         upDM = cmds.createNode("decomposeMatrix", n=f"{up}_zipper_DM")
    #         loDM = cmds.createNode("decomposeMatrix", n=f"{lo}_zipper_DM")
    #         upTXMD = cmds.createNode("multiplyDivide", n=f"{up}_zipper_TX_MD")
    #         upRXMD = cmds.createNode("multiplyDivide", n=f"{up}_zipper_RX_MD")
    #         loTXMD = cmds.createNode("multiplyDivide", n=f"{lo}_zipper_TX_MD")
    #         loRXMD = cmds.createNode("multiplyDivide", n=f"{lo}_zipper_RX_MD")
    #         upRV = cmds.createNode("remapValue", n=f"{up}_zipper_RV")
    #         loRV = cmds.createNode("remapValue", n=f"{lo}_zipper_RV")
            
    #         cmds.connectAttr(f"{upOffsets[index]}.worldMatrix[0]", f"{upMM}.matrixIn[0]")
    #         cmds.connectAttr(f"{upLocZippers[index]}.worldInverseMatrix[0]", f"{upMM}.matrixIn[1]")
    #         cmds.connectAttr(f"{upMM}.matrixSum", f"{upDM}.inputMatrix")
    #         cmds.connectAttr(f"{upDM}.outputTranslate", f"{upTXMD}.input1")
    #         cmds.connectAttr(f"{upDM}.outputRotate", f"{upRXMD}.input1")
    #         cmds.connectAttr(f"{mouthCtrl}.zipper", f"{upRV}.inputValue")

    #         cmds.connectAttr(f"{loOffsets[index]}.worldMatrix[0]", f"{loMM}.matrixIn[0]")
    #         cmds.connectAttr(f"{loLocZippers[index]}.worldInverseMatrix[0]", f"{loMM}.matrixIn[1]")
    #         cmds.connectAttr(f"{loMM}.matrixSum", f"{loDM}.inputMatrix")
    #         cmds.connectAttr(f"{loDM}.outputTranslate", f"{loTXMD}.input1")
    #         cmds.connectAttr(f"{loDM}.outputRotate", f"{loRXMD}.input1")
    #         cmds.connectAttr(f"{mouthCtrl}.zipper", f"{loRV}.inputValue")

    #         cmds.setAttr(f"{upRV}.outputMax", 2.0)
    #         cmds.setAttr(f"{loRV}.outputMax", 2.0)


    #         for i in ["input2X","input2Y", "input2Z"]:
    #             cmds.connectAttr(f"{upRV}.outValue", f"{upTXMD}.{i}")
    #             cmds.connectAttr(f"{upRV}.outValue", f"{upRXMD}.{i}")
    #             cmds.connectAttr(f"{loRV}.outValue", f"{loTXMD}.{i}")
    #             cmds.connectAttr(f"{loRV}.outValue", f"{loRXMD}.{i}")

    #         cmds.connectAttr(f"{upTXMD}.output.outputY", f"{upZippers[index]}.translate.translateY")
    #         cmds.connectAttr(f"{upOffsets[index]}.translate.translateX", f"{upZippers[index]}.translate.translateX")
    #         cmds.connectAttr(f"{upOffsets[index]}.translate.translateZ", f"{upZippers[index]}.translate.translateZ")
    #         cmds.connectAttr(f"{upRXMD}.output", f"{upZippers[index]}.rotate")
    #         # cmds.connectAttr(f"{upRXMD}.output.outputX", f"{upZippers[index]}.rotate.rotateX")
    #         # cmds.connectAttr(f"{upOffsets[index]}.rotate.rotateY", f"{upZippers[index]}.rotate.rotateY")
    #         # cmds.connectAttr(f"{upOffsets[index]}.rotate.rotateZ", f"{upZippers[index]}.rotate.rotateZ")

    #         cmds.connectAttr(f"{loTXMD}.output.outputY", f"{loZippers[index]}.translate.translateY")
    #         cmds.connectAttr(f"{loOffsets[index]}.translate.translateX", f"{loZippers[index]}.translate.translateX")
    #         cmds.connectAttr(f"{loOffsets[index]}.translate.translateZ", f"{loZippers[index]}.translate.translateZ")
    #         cmds.connectAttr(f"{loRXMD}.output", f"{loZippers[index]}.rotate")
    #         # cmds.connectAttr(f"{loRXMD}.output.outputX", f"{loZippers[index]}.rotate.rotateX")
    #         # cmds.connectAttr(f"{loOffsets[index]}.rotate.rotateY", f"{loZippers[index]}.rotate.rotateY")
    #         # cmds.connectAttr(f"{loOffsets[index]}.rotate.rotateZ", f"{loZippers[index]}.rotate.rotateZ")

    #         if rangeCatch >= (rangeSetInfl * (rangeSet+1)):
    #             print("READ THE CATCH OVERRIDE")
    #             rangeCatch = rangeSetInfl

    #         if up in upLipJoints[(rangeSet+1)::]:
    #             diff = 2.0 - rangeCatch
    #             cmds.setAttr(f"{upRV}.inputMin", rangeCatch)                
    #             cmds.setAttr(f"{upRV}.inputMax", diff)
    #             cmds.setAttr(f"{loRV}.inputMin", rangeCatch)                
    #             cmds.setAttr(f"{loRV}.inputMax", diff)
    #             #rangeCatch+=rangeSetInfl
    #         elif up in upLipJoints[:rangeSet:]:
    #             diff = 2.0 - rangeCatch
    #             cmds.setAttr(f"{upRV}.inputMin", rangeCatch)                
    #             cmds.setAttr(f"{upRV}.inputMax", diff)
    #             cmds.setAttr(f"{loRV}.inputMin", rangeCatch)                
    #             cmds.setAttr(f"{loRV}.inputMax", diff)
    #             #rangeCatch+=rangeSetInfl
    #         else:
    #             rangeCatch=0
    #             cmds.setAttr(f"{upRV}.inputMin", 0)                
    #             cmds.setAttr(f"{upRV}.inputMax", 2)
    #             cmds.setAttr(f"{loRV}.inputMin", 0)                
    #             cmds.setAttr(f"{loRV}.inputMax", 2)
    #         rangeCatch+=rangeSetInfl 

    #         index+=1

    #     # Cleanup
    #     # Parent joints
    #     jointGroup = cmds.createNode("transform", n=f"{self.side}_{self.label}_jointGroup")
    #     for i in [upLipJoints, loLipJoints, cornerJoints]:            
    #         cmds.parent(i, jointGroup)

    #     cmds.parent(jointGroup, self.moduleUtilities)
    #     cmds.parent(lGroup, self.plugParent)
    #     cmds.parent(rGroup, self.plugParent)
    #     cmds.parent([mouthPar, upMouthPar, loMouthPar], self.plugParent)
    #     cmds.parent([upMiddlePar, loMiddlePar], self.plugParent)
    #     rangeIndex = (len(upParents) - 1) / 2
    #     cmds.parent([upParents[int(rangeIndex)], loParents[int(rangeIndex)]], self.plugParent)        

    #     self.addSocketMetaData()

    # def easeInOutSine(self, input = 1.0):
    #     return -(m.cos(m.pi * input) - 1.0) / 2.0

    # def easeOutCubic(self, input = 1.0):
    #     return 1 - m.pow(1.0 - input, 3.0)
    
    # def easeInCubic(self, input = 1.0):
    #     return input * input * input
    
    # def easeInCirc(self, input = 1.0):
    #     return 1 - m.sqrt(1 - m.pow(input, 2))
    
    # def easeInSine(self, input = 1.0):
    #     return 1 - m.cos((input*m.pi)/2)
    
    # @staticmethod
    # def getModuleDetails():
    #     # Print relevant doc information for this module
    #     return print('''
    #     This module functions as described below. . . 

    #     The LIPS module is a multi side module which will encompass a L, R, M side labelling; this cannot be overridden.
    #     There are also a few -gotchas- that the module works around such as. . .
    #         1 ) There must be an odd number of lip joints, if there are not an odd number the module will ADD
    #             another lip to compensate. This is because multiple layers of nodes depend on an M lip and L / R corner
    #             lip to function.
    #         2) The L R M naming for sides cannot be edited at this time, this will be a feature added in the future.
              
    #         3) There are a few transform based bugs with the zipper function when using the mouth / jaw
              
    #     How the LIPS work.
    #           CONTROLS
    #           1 ) There are several LOCAL lip CONTROLs which dictate the xforms of the JOINTs.
              
    #           2 ) There are a set of MAIN CORNER CONTROLs and UP / LO lip CONTROLs which position the LOCAL CONTROLs
    #               along as EASING mathmatical curve (there is no CV curve in the scene).
              
    #           3 ) The LOCAL CONTROLs aim and the previous sequencial LOCAL unless they are the CORNER or MIDDLE LOCALs. 
    #               The MIDDLE LOCALs are a PTC to the relevant MAIN CONTROL and the CORNERs OC between the previous sequencial 
    #               LOCAL CONTROLs
              
    #           4 ) The MOUTH CONTROLs are comprised of a PRIMARY MOUTH, UP MOUTH and LO MOUTH.
    #               The PRIMARY moves all CONTROLs of the module in a parent relationship 
    #               UP and LO PRIMARY CONTROLs xform the MAIN CONTROLs using PTCs
              
    #           5 ) The PRIMARY MOUTH has a zipper attribute which will return all LOCAL CONTROLs to their default position
    #               in a cascade method. 
    #     ''')

    # @staticmethod
    # def getModuleHelp():
    #     # Print all mutable arguments and guidelines for the module.
    #     return print('''
    #     The following variables edit the module functions
    #         VARIABLES:
    #             rig: ...

    #             side: A String dictating the side of the motion system (usually L, R, or M)
                     
    #             label: A string dicating the name of the module... (Arm, Leg, Spine, ect.)
                     
    #             ctrlShapes: A string which dictates the motion control shape, available options are...
    #                         "circle", "square", "box", "sphere"
    #                         This variable has a default loaded for the module, changing it could result in 
    #                         unpredictable curve alignments

    #             ctrlScale: By default "None", this can be edited as a list of 3 floats to change the scaleling of all controls

    #             numberOfJoints: The total number of joints across each upper and lower lip array. Must be Odd, if the input
    #                             value is not odd it will append 1 to the value.
                
    #             lipSegments: The total number of MAIN controls across the lips. Functions with 3 as a standard. 
                     
    #             jawTarget: A string which will constrain the lips to a jaw target and allow the mouth to open with a jaw.
    #                        This is by default "None" and is not a required parameter.
                     
    #     ''')