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
        wsParent = cmds.createNode("transform", n=f"{self.side}_{self.label}_WorldSpace", p=self.plugParent)
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

        cornerJoints = [] # For corners, 0 In, 1 Out
        upLidJoints = [] # All up lips minus the corners
        loLidJoints = [] # All lo lips minus the corners

        # Making joints from proxy positions. 
        index = 1
        for u, l in zip(fullRangeUpLabels[1:-1:], fullRangeLoLabels[1:-1:]):
            uLabel = f"{self.side}_{self.label}_{u}"
            lLabel = f"{self.side}_{self.label}_{l}"
            uJnt = cmds.createNode("joint", n=uLabel, p=self.moduleUtilities)
            lJnt = cmds.createNode("joint", n=lLabel, p=self.moduleUtilities)

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
        iJnt = cmds.createNode("joint", n=inLabel, p=self.moduleUtilities)
        oJnt = cmds.createNode("joint", n=outLabel, p=self.moduleUtilities)
        cornerJoints.extend([iJnt, oJnt])
        cmds.xform(iJnt, ws=True, t=cmds.xform(
                f"{self.side}_{self.label}_{fullRangeUp[0]}", q=True, ws=True, t=True
            ))
        cmds.xform(oJnt, ws=True, t=cmds.xform(
                f"{self.side}_{self.label}_{fullRangeUp[-1]}", q=True, ws=True, t=True
            ))

        eyejoint = cmds.createNode("joint", n=f"{self.side}_{self.label}_{self.proxies['Eyeball'].name}", p=self.moduleUtilities)
        cmds.xform(eyejoint, ws=True, t=cmds.xform(
                f"{self.side}_{self.label}_{self.proxies['Eyeball'].name}_proxy", q=True, ws=True, t=True
            ))
        
        for u, l in zip(upLidJoints, loLidJoints):
            self.bindJoints[u] = eyejoint
            self.bindJoints[l] = eyejoint
            self.sockets[u] = u
            self.sockets[l] = l
        self.bindJoints[iJnt] = eyejoint
        self.bindJoints[oJnt] = eyejoint
        self.bindJoints[eyejoint] = None
        self.sockets[iJnt] = iJnt
        self.sockets[oJnt] = oJnt
        self.sockets[eyejoint] = None

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
            uGrp = cmds.createNode("transform", n=f"{u}_grp", p=self.worldParent)
            lGrp = cmds.createNode("transform", n=f"{l}_grp", p=self.worldParent)
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
            ptc = cmds.parentConstraint(uCtrl, u, n=f"{u}_PTC", mo=0)
            ptc = cmds.parentConstraint(lCtrl, l, n=f"{l}_PTC", mo=0)

        for c in cornerJoints:
            cGrp = cmds.createNode("transform", n=f"{c}_grp", p=self.worldParent)
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
            ptc = cmds.parentConstraint(cCtrl, c, n=f"{cCtrl}_PTC", mo=0)

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
            folGroup = cmds.createNode("transform", n=f"{self.side}_{self.label}_follicles", p=self.moduleUtilities)
            index = 0
            if useMesh:
                ifol = cmds.createNode("transform", n=f"{cornerJoints[0]}_fol", p=folGroup)
                ifolShape = cmds.createNode("follicle", n=f"{cornerJoints[0]}_folShape", p=ifol)
                ofol = cmds.createNode("transform", n=f"{cornerJoints[1]}_fol", p=folGroup)
                ofolShape = cmds.createNode("follicle", n=f"{cornerJoints[1]}_folShape", p=ofol)
                cmds.setAttr(f"{ifolShape}.visibility", 0, l=True, k=False)
                cmds.setAttr(f"{ofolShape}.visibility", 0, l=True, k=False)
            # IN
                icpom = cmds.createNode("closestPointOnMesh", n=f"{cornerFolOffsets[0]}_CPOM")
                cmds.connectAttr(
                    f"{self.follicleMesh}.worldMatrix[0]", f"{ifolShape}.inputWorldMatrix", f=True)
                cmds.connectAttr(f"{self.follicleMesh}.outMesh",
                                f"{ifolShape}.inputMesh", f=True)
                # ucpom connections
                iDM = cmds.createNode("decomposeMatrix", n=f"{cornerGroups[0]}_DM")
                cmds.connectAttr(f"{cornerGroups[0]}.worldMatrix[0]", f"{iDM}.inputMatrix")
                cmds.connectAttr(f"{iDM}.outputTranslate", f"{icpom}.inPosition")
                cmds.connectAttr(f"{icpom}.parameterU", f"{ifolShape}.parameterU")
                cmds.connectAttr(f"{icpom}.parameterV", f"{ifolShape}.parameterV")
                cmds.connectAttr(f"{ifolShape}.outTranslate", f"{ifol}.translate")
                cmds.connectAttr(f"{ifolShape}.outRotate", f"{ifol}.rotate")
                # cmds.connectAttr(f"{ufol}.translate", f"{uf}.translate")
                
                cmds.connectAttr(f"{self.follicleMesh}.outMesh", f"{icpom}.inMesh")
                cmds.connectAttr(f"{self.follicleMesh}.worldMatrix[0]", f"{icpom}.inputMatrix")
                pc = cmds.pointConstraint(ifol, cornerFolOffsets[0], mo=1)
                
                # LO
                ocpom = cmds.createNode("closestPointOnMesh", n=f"{cornerFolOffsets[1]}_CPOM")
                cmds.connectAttr(
                    f"{self.follicleMesh}.worldMatrix[0]", f"{ofolShape}.inputWorldMatrix", f=True)
                cmds.connectAttr(f"{self.follicleMesh}.outMesh",
                                f"{ofolShape}.inputMesh", f=True)
                # ucpom connections
                oDM = cmds.createNode("decomposeMatrix", n=f"{cornerGroups[1]}_DM")
                cmds.connectAttr(f"{cornerGroups[1]}.worldMatrix[0]", f"{oDM}.inputMatrix")
                cmds.connectAttr(f"{oDM}.outputTranslate", f"{ocpom}.inPosition")
                cmds.connectAttr(f"{ocpom}.parameterU", f"{ofolShape}.parameterU")
                cmds.connectAttr(f"{ocpom}.parameterV", f"{ofolShape}.parameterV")
                cmds.connectAttr(f"{ofolShape}.outTranslate", f"{ofol}.translate")
                cmds.connectAttr(f"{ofolShape}.outRotate", f"{ofol}.rotate")
                # cmds.connectAttr(f"{ufol}.translate", f"{uf}.translate")
                
                cmds.connectAttr(f"{self.follicleMesh}.outMesh", f"{ocpom}.inMesh")
                cmds.connectAttr(f"{self.follicleMesh}.worldMatrix[0]", f"{ocpom}.inputMatrix")
                pc = cmds.pointConstraint(ofol, cornerFolOffsets[1], mo=1)

            for uf, lf in zip(upFolOffsets, loFolOffsets):
                ufol = cmds.createNode("transform", n=f"{upLidJoints[index]}_fol", p=folGroup)
                ufolShape = cmds.createNode("follicle", n=f"{upLidJoints[index]}_folShape", p=ufol)
                lfol = cmds.createNode("transform", n=f"{loLidJoints[index]}_fol", p=folGroup)
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
        else:
            cmds.parent(upGroups, self.plugParent)
            cmds.parent(loGroups, self.plugParent)
            cmds.parent(cornerGroups, self.plugParent)

        upMainPar = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['Up'].name}Main_grp", 
                                    p=self.plugParent)
        upMainCtrl = cmds.createNode("transform", 
                                     n=f"{self.side}_{self.label}_{self.proxies['Up'].name}Main_CTRL", p=upMainPar)
        upMainCtrlShape = ctrlCrv.Ctrl(
                node=upMainCtrl,
                shape="sphere",
                scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
                offset=[0, 0, 0]
            )
        upMainCtrlShape.giveCtrlShape()
        loMainPar = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['Lo'].name}Main_grp", 
                                    p=self.plugParent)
        loMainCtrl = cmds.createNode("transform", 
                                     n=f"{self.side}_{self.label}_{self.proxies['Lo'].name}Main_CTRL", p=loMainPar)
        loMainCtrlShape = ctrlCrv.Ctrl(
                node=loMainCtrl,
                shape="sphere",
                scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
                offset=[0, 0, 0]
            )
        loMainCtrlShape.giveCtrlShape()
        inMainPar = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['In'].name}Main_grp", 
                                    p=self.plugParent)
        inMainCtrl = cmds.createNode("transform", 
                                     n=f"{self.side}_{self.label}_{self.proxies['In'].name}Main_CTRL", p=inMainPar)
        inMainCtrlShape = ctrlCrv.Ctrl(
                node=inMainCtrl,
                shape="sphere",
                scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
                offset=[0, 0, 0]
            )
        inMainCtrlShape.giveCtrlShape()
        outMainPar = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['Out'].name}Main_grp", 
                                     p=self.plugParent)
        outMainCtrl = cmds.createNode("transform", 
                                     n=f"{self.side}_{self.label}_{self.proxies['Out'].name}Main_CTRL", p=outMainPar)
        outMainCtrlShape = ctrlCrv.Ctrl(
                node=outMainCtrl,
                shape="sphere",
                scale=[self.ctrlScale[0] * 1.25, self.ctrlScale[1] * 1.25, self.ctrlScale[2] * 1.25],
                offset=[0, 0, 0]
            )
        outMainCtrlShape.giveCtrlShape()

        if not self.follicleMesh or self.follicleSurface:
            upTrack = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['Up'].name}Main_track", p=upMainPar)
            cmds.parent(upMainCtrl, upTrack)
            loTrack = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['Lo'].name}Main_track", p=loMainPar)
            cmds.parent(loMainCtrl, loTrack)
            inTrack = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['In'].name}Main_track", p=inMainPar)
            cmds.parent(inMainCtrl, inTrack)
            outTrack = cmds.createNode("transform", n=f"{self.side}_{self.label}_{self.proxies['Out'].name}Main_track", p=outMainPar)
            cmds.parent(outMainCtrl, outTrack)           

        cmds.xform(upMainPar, ws=True, t=cmds.xform(
            f"{self.side}_{self.label}_{self.proxies['Up'].name}_proxy", q=True, ws=True, t=True
        ))
        cmds.xform(loMainPar, ws=True, m=cmds.xform(
            f"{self.side}_{self.label}_{self.proxies['Lo'].name}_proxy", q=True, ws=True, m=True
        ))
        cmds.xform(inMainPar, ws=True, m=cmds.xform(
            f"{self.side}_{self.label}_{self.proxies['In'].name}_proxy", q=True, ws=True, m=True
        ))
        cmds.xform(outMainPar, ws=True, m=cmds.xform(
            f"{self.side}_{self.label}_{self.proxies['Out'].name}_proxy", q=True, ws=True, m=True
        ))

        if not self.follicleMesh or self.follicleSurface:
            rangeLen = len(fullRangeUpLabels)
            if rangeLen % 2 == 0:
                pass
            else:
                rangeLen-=1
            halfLen = rangeLen / 2
            inflRate = 1 / (halfLen-1)
            inflVal = 0.0

            for up, lo in zip(fullRangeUpLabels, fullRangeLoLabels):
                upTarget = f"{self.side}_{self.label}_{up}_folOffset"
                loTarget = f"{self.side}_{self.label}_{lo}_folOffset"
                if inflVal >= 1.0:
                    inflVal = 1.0 # Catch for middle point and prevents overvalue
                
                if up == fullRangeUpLabels[0]:
                    # Do In Corner hookup
                    cmds.connectAttr(f"{inMainCtrl}.translate", f"{upTarget}.translate")
                    inflVal+=inflRate
                    pass
                elif up == fullRangeUpLabels[-1]:
                    # Do Out Corner hookup
                    cmds.connectAttr(f"{outMainCtrl}.translate", f"{upTarget}.translate")
                    inflVal-=inflRate
                    pass
                else:
                    if up in fullRangeUpLabels[int(halfLen)::]:
                        # Do outer half
                        uMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{up}Fol_MD")
                        lMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{lo}Fol_MD")
                        cMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{up}Fol_In_MD")
                        uPMA = cmds.createNode("plusMinusAverage", n=f"{self.side}_{self.label}_{up}Fol_PMA")
                        lPMA = cmds.createNode("plusMinusAverage", n=f"{self.side}_{self.label}_{lo}Fol_PMA")
                        # Up Connections
                        cmds.connectAttr(f"{upTrack}.translate", f"{uMD}.input1")
                        cmds.connectAttr(f"{outTrack}.translate", f"{cMD}.input1")
                        cmds.connectAttr(f"{uMD}.output", f"{uPMA}.input3D[0]")
                        cmds.connectAttr(f"{cMD}.output", f"{uPMA}.input3D[1]")
                        cmds.connectAttr(f"{uPMA}.output3D", f"{upTarget}.translate")
                        # Up set
                        cmds.setAttr(f"{uMD}.input2X", self.easeInCubic(inflVal))
                        cmds.setAttr(f"{uMD}.input2Y", self.easeInCubic(inflVal))
                        cmds.setAttr(f"{uMD}.input2Z", self.easeInSine(inflVal))
                        cmds.setAttr(f"{cMD}.input2X", (1-self.easeInCubic(inflVal)))
                        cmds.setAttr(f"{cMD}.input2Y", (1-self.easeInCubic(inflVal)))
                        cmds.setAttr(f"{cMD}.input2Z", (1-self.easeInSine(inflVal)))
                        # Lo Connections
                        cmds.connectAttr(f"{loTrack}.translate", f"{lMD}.input1")
                        cmds.connectAttr(f"{lMD}.output", f"{lPMA}.input3D[0]")
                        cmds.connectAttr(f"{cMD}.output", f"{lPMA}.input3D[1]")
                        cmds.connectAttr(f"{lPMA}.output3D", f"{loTarget}.translate")
                        # Lo set
                        cmds.setAttr(f"{lMD}.input2X", self.easeInCubic(inflVal))
                        cmds.setAttr(f"{lMD}.input2Y", self.easeInCubic(inflVal))
                        cmds.setAttr(f"{lMD}.input2Z", self.easeInSine(inflVal))
                        cmds.setAttr(f"{cMD}.input2X", (1-self.easeInCubic(inflVal)))
                        cmds.setAttr(f"{cMD}.input2Y", (1-self.easeInCubic(inflVal)))
                        cmds.setAttr(f"{cMD}.input2Z", (1-self.easeInSine(inflVal)))
                        inflVal-=inflRate
                    else:
                        # Do inner half
                        uMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{up}_MD")
                        lMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{lo}_MD")
                        cMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{up}_In_MD")
                        uPMA = cmds.createNode("plusMinusAverage", n=f"{self.side}_{self.label}_{up}_PMA")
                        lPMA = cmds.createNode("plusMinusAverage", n=f"{self.side}_{self.label}_{lo}_PMA")
                        # Up Connections
                        cmds.connectAttr(f"{upTrack}.translate", f"{uMD}.input1")
                        cmds.connectAttr(f"{inTrack}.translate", f"{cMD}.input1")
                        cmds.connectAttr(f"{uMD}.output", f"{uPMA}.input3D[0]")
                        cmds.connectAttr(f"{cMD}.output", f"{uPMA}.input3D[1]")
                        cmds.connectAttr(f"{uPMA}.output3D", f"{upTarget}.translate")
                        # Up set
                        cmds.setAttr(f"{uMD}.input2X", self.easeInCubic(inflVal))
                        cmds.setAttr(f"{uMD}.input2Y", self.easeInCubic(inflVal))
                        cmds.setAttr(f"{uMD}.input2Z", self.easeInSine(inflVal))
                        # Lo Connections
                        cmds.connectAttr(f"{loTrack}.translate", f"{lMD}.input1")
                        cmds.connectAttr(f"{lMD}.output", f"{lPMA}.input3D[0]")
                        cmds.connectAttr(f"{cMD}.output", f"{lPMA}.input3D[1]")
                        cmds.connectAttr(f"{lPMA}.output3D", f"{loTarget}.translate")
                        # Lo set
                        cmds.setAttr(f"{lMD}.input2X", self.easeInCubic(inflVal))
                        cmds.setAttr(f"{lMD}.input2Y", self.easeInCubic(inflVal))
                        cmds.setAttr(f"{lMD}.input2Z", self.easeInSine(inflVal))
                        inflVal+=inflRate

        rangeLen = len(fullRangeUpLabels)
        if rangeLen % 2 == 0:
            pass
        else:
            rangeLen-=1
        halfLen = rangeLen / 2
        inflRate = 1 / (halfLen-1)
        inflVal = 0.0

        for up, lo in zip(fullRangeUpLabels, fullRangeLoLabels):
            upTarget = f"{self.side}_{self.label}_{up}_easeOffset"
            loTarget = f"{self.side}_{self.label}_{lo}_easeOffset"
            if inflVal >= 1.0:
                inflVal = 1.0 # Catch for middle point and prevents overvalue
            
            if up == fullRangeUpLabels[0]:
                # Do In Corner hookup
                cmds.connectAttr(f"{inMainCtrl}.translate", f"{upTarget}.translate")
                inflVal+=inflRate
                pass
            elif up == fullRangeUpLabels[-1]:
                # Do Out Corner hookup
                cmds.connectAttr(f"{outMainCtrl}.translate", f"{upTarget}.translate")
                inflVal-=inflRate
                pass
            else:
                if up in fullRangeUpLabels[int(halfLen)::]:
                    # Do outer half
                    uMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{up}_MD")
                    lMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{lo}_MD")
                    cMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{up}_In_MD")
                    uPMA = cmds.createNode("plusMinusAverage", n=f"{self.side}_{self.label}_{up}_PMA")
                    lPMA = cmds.createNode("plusMinusAverage", n=f"{self.side}_{self.label}_{lo}_PMA")
                    # Up Connections
                    cmds.connectAttr(f"{upMainCtrl}.translate", f"{uMD}.input1")
                    cmds.connectAttr(f"{outMainCtrl}.translate", f"{cMD}.input1")
                    cmds.connectAttr(f"{uMD}.output", f"{uPMA}.input3D[0]")
                    cmds.connectAttr(f"{cMD}.output", f"{uPMA}.input3D[1]")
                    cmds.connectAttr(f"{uPMA}.output3D", f"{upTarget}.translate")
                    # Up set
                    cmds.setAttr(f"{uMD}.input2X", self.easeInCubic(inflVal))
                    cmds.setAttr(f"{uMD}.input2Y", self.easeInCubic(inflVal))
                    cmds.setAttr(f"{uMD}.input2Z", self.easeInSine(inflVal))
                    cmds.setAttr(f"{cMD}.input2X", (1-self.easeInCubic(inflVal)))
                    cmds.setAttr(f"{cMD}.input2Y", (1-self.easeInCubic(inflVal)))
                    cmds.setAttr(f"{cMD}.input2Z", (1-self.easeInSine(inflVal)))
                    # Lo Connections
                    cmds.connectAttr(f"{loMainCtrl}.translate", f"{lMD}.input1")
                    cmds.connectAttr(f"{lMD}.output", f"{lPMA}.input3D[0]")
                    cmds.connectAttr(f"{cMD}.output", f"{lPMA}.input3D[1]")
                    cmds.connectAttr(f"{lPMA}.output3D", f"{loTarget}.translate")
                    # Lo set
                    cmds.setAttr(f"{lMD}.input2X", self.easeInCubic(inflVal))
                    cmds.setAttr(f"{lMD}.input2Y", self.easeInCubic(inflVal))
                    cmds.setAttr(f"{lMD}.input2Z", self.easeInSine(inflVal))
                    cmds.setAttr(f"{cMD}.input2X", (1-self.easeInCubic(inflVal)))
                    cmds.setAttr(f"{cMD}.input2Y", (1-self.easeInCubic(inflVal)))
                    cmds.setAttr(f"{cMD}.input2Z", (1-self.easeInSine(inflVal)))
                    inflVal-=inflRate
                else:
                    # Do inner half
                    uMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{up}_MD")
                    lMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{lo}_MD")
                    cMD = cmds.createNode("multiplyDivide", n=f"{self.side}_{self.label}_{up}_In_MD")
                    uPMA = cmds.createNode("plusMinusAverage", n=f"{self.side}_{self.label}_{up}_PMA")
                    lPMA = cmds.createNode("plusMinusAverage", n=f"{self.side}_{self.label}_{lo}_PMA")
                    # Up Connections
                    cmds.connectAttr(f"{upMainCtrl}.translate", f"{uMD}.input1")
                    cmds.connectAttr(f"{inMainCtrl}.translate", f"{cMD}.input1")
                    cmds.connectAttr(f"{uMD}.output", f"{uPMA}.input3D[0]")
                    cmds.connectAttr(f"{cMD}.output", f"{uPMA}.input3D[1]")
                    cmds.connectAttr(f"{uPMA}.output3D", f"{upTarget}.translate")
                    # Up set
                    cmds.setAttr(f"{uMD}.input2X", self.easeInCubic(inflVal))
                    cmds.setAttr(f"{uMD}.input2Y", self.easeInCubic(inflVal))
                    cmds.setAttr(f"{uMD}.input2Z", self.easeInSine(inflVal))
                    # Lo Connections
                    cmds.connectAttr(f"{loMainCtrl}.translate", f"{lMD}.input1")
                    cmds.connectAttr(f"{lMD}.output", f"{lPMA}.input3D[0]")
                    cmds.connectAttr(f"{cMD}.output", f"{lPMA}.input3D[1]")
                    cmds.connectAttr(f"{lPMA}.output3D", f"{loTarget}.translate")
                    # Lo set
                    cmds.setAttr(f"{lMD}.input2X", self.easeInCubic(inflVal))
                    cmds.setAttr(f"{lMD}.input2Y", self.easeInCubic(inflVal))
                    cmds.setAttr(f"{lMD}.input2Z", self.easeInSine(inflVal))
                    inflVal+=inflRate
        cmds.addAttr(upMainCtrl, ln="blink", at="float", min=0.0, max=1.0, dv=0, k=True)
        cmds.addAttr(upMainCtrl, ln="blinkLine", at="float", min=0.0, max=1.0, dv=0.25, k=True)
        for i in [inMainCtrl, loMainCtrl, outMainCtrl]:
            cmds.addAttr(i, ln="blink",
                         proxy=f"{upMainCtrl}.blink", at="float", min=0.0, max=1.0, dv=0, k=True)
            cmds.addAttr(i, ln="blinkLine",
                         proxy=f"{upMainCtrl}.blinkLine", at="float", min=0.0, max=1.0, dv=0.5, k=True)
        index = 0
        for uPar, lPar in zip(upGroups, loGroups):
            # do PMA blend for each lid.
            lineBC = cmds.createNode("blendColors", n=f"{self.side}_{self.label}_{index}_BC")
            uBC = cmds.createNode("blendColors", n=f"{uPar}_Blink_BC")
            lBC = cmds.createNode("blendColors", n=f"{lPar}_Blink_BC")

            cmds.connectAttr(f"{upMainCtrl}.blink", f"{uBC}.blender")
            cmds.connectAttr(f"{upMainCtrl}.blink", f"{lBC}.blender")
            cmds.connectAttr(f"{upMainCtrl}.blinkLine", f"{lineBC}.blender")

            uT = cmds.xform(uPar, q=True, ws=True, t=True)
            lT = cmds.xform(lPar, q=True, ws=True, t=True)
            xformIndex = 0
            for rgb in ["R", "G", "B"]:
                cmds.setAttr(f"{lineBC}.color1{rgb}", uT[xformIndex])
                cmds.setAttr(f"{lineBC}.color2{rgb}", lT[xformIndex])
                cmds.setAttr(f"{uBC}.color2{rgb}", uT[xformIndex])
                cmds.setAttr(f"{lBC}.color2{rgb}", lT[xformIndex])
                xformIndex+=1
            cmds.connectAttr(f"{lineBC}.output", f"{uBC}.color1")
            cmds.connectAttr(f"{lineBC}.output", f"{lBC}.color1")
            cmds.connectAttr(f"{uBC}.output", f"{uPar}.translate")
            cmds.connectAttr(f"{lBC}.output", f"{lPar}.translate")
            index+=1

        eyePar = cmds.createNode("transform", n=f"{eyejoint}_grp", p=self.plugParent)
        eyeCtrl = cmds.createNode('transform', n=f"{eyejoint}_CTRL", p=eyePar)
        ptc = cmds.parentConstraint(eyeCtrl, eyejoint, n=f"{eyejoint}_PTC", mo=0)
        eyeCtrlShape = ctrlCrv.Ctrl(
                node=eyeCtrl,
                shape="sphere",
                scale=[self.ctrlScale[0] * 5, self.ctrlScale[1] * 5, self.ctrlScale[2] * 5],
                offset=[0, 0, 0]
            )
        eyeCtrlShape.giveCtrlShape()
        if not self.follicleMesh or self.follicleSurface:
            ptc = cmds.parentConstraint([eyeCtrl, upMainPar], upTrack, n=f"{upTrack}_PTC", mo=1)[0]
            cmds.setAttr(f"{ptc}.interpType", 2)
            cmds.setAttr(f"{ptc}.{upMainPar}W1", 4)
            ptc = cmds.parentConstraint([eyeCtrl, loMainPar], loTrack, n=f"{loTrack}_PTC", mo=1)[0]
            cmds.setAttr(f"{ptc}.interpType", 2)
            cmds.setAttr(f"{ptc}.{loMainPar}W1", 4)

    def easeInCubic(self, input = 1.0):
        return input * input * input
    
    def easeInSine(self, input = 1.0):
        return 1 - m.cos((input*m.pi)/2)          

    
    @staticmethod
    def getModuleDetails():
        # Print relevant doc information for this module
        return print('''
        This module functions as described below. . . 

        The LIPS module is a multi side module which will encompass a L, R, M side labelling; this cannot be overridden.
        There are also a few -gotchas- that the module works around such as. . .
            1 ) There must be an odd number of lip joints, if there are not an odd number the module will ADD
                another lip to compensate. This is because multiple layers of nodes depend on an M lip and L / R corner
                lip to function.
            2) The L R M naming for sides cannot be edited at this time, this will be a feature added in the future.
              
            3) There are a few transform based bugs with the zipper function when using the mouth / jaw
              
        How the LIPS work.
              CONTROLS
              1 ) There are several LOCAL lip CONTROLs which dictate the xforms of the JOINTs.
              
              2 ) There are a set of MAIN CORNER CONTROLs and UP / LO lip CONTROLs which position the LOCAL CONTROLs
                  along as EASING mathmatical curve (there is no CV curve in the scene).
              
              3 ) The LOCAL CONTROLs aim and the previous sequencial LOCAL unless they are the CORNER or MIDDLE LOCALs. 
                  The MIDDLE LOCALs are a PTC to the relevant MAIN CONTROL and the CORNERs OC between the previous sequencial 
                  LOCAL CONTROLs
              
              4 ) The MOUTH CONTROLs are comprised of a PRIMARY MOUTH, UP MOUTH and LO MOUTH.
                  The PRIMARY moves all CONTROLs of the module in a parent relationship 
                  UP and LO PRIMARY CONTROLs xform the MAIN CONTROLs using PTCs
              
              5 ) The PRIMARY MOUTH has a zipper attribute which will return all LOCAL CONTROLs to their default position
                  in a cascade method. 
        ''')

    @staticmethod
    def getModuleHelp():
        # Print all mutable arguments and guidelines for the module.
        return print('''
        The following variables edit the module functions
            VARIABLES:
                rig: ...

                side: A String dictating the side of the motion system (usually L, R, or M)
                     
                label: A string dicating the name of the module... (Arm, Leg, Spine, ect.)
                     
                ctrlShapes: A string which dictates the motion control shape, available options are...
                            "circle", "square", "box", "sphere"
                            This variable has a default loaded for the module, changing it could result in 
                            unpredictable curve alignments

                ctrlScale: By default "None", this can be edited as a list of 3 floats to change the scaleling of all controls

                numberOfJoints: The total number of joints across each upper and lower lip array. Must be Odd, if the input
                                value is not odd it will append 1 to the value.
                
                lipSegments: The total number of MAIN controls across the lips. Functions with 3 as a standard. 
                     
                jawTarget: A string which will constrain the lips to a jaw target and allow the mouth to open with a jaw.
                           This is by default "None" and is not a required parameter.
                     
        ''')