import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds


class RibbonBindIK(motionBase.MotionModuleBase):
    """Root Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="sphere", ctrlScale=None, addOffset=True, spans=5,
                 reverse=True, meta=True, numberOfJoints=10, localAxisTranslate = "X", buildOrder: int = 2000, 
                 isMuted: bool = False, parent: str = None, mirror: bool = False, bypassProxiesOnly: bool = True, 
                 selectedPlug: str = "", selectedSocket: str = "", aimAxis: str = "+x", upAxis: str = "-z") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, 
                         parent, mirror, bypassProxiesOnly, selectedPlug, 
                         selectedSocket, aimAxis, upAxis)

        if ctrlScale is None:
            ctrlScale = [1.0, 1.0, 1.0]

        self.addOffset = addOffset
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        self.spans = spans
        self.reverse = reverse
        self.meta = meta
        self.numberOfJoints = numberOfJoints
        self.upVector = None

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
        if self.spans > 1:
            par = "Start"
            for i in range(1, self.spans):
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

            self.proxies["End"].parent = str(self.spans - 1)
        
        self.plugs = {
            "Local": None,
            "World": None
        }
        # if self.segments > 1:
        #     for i in range(1, self.segments):
        #         self.socket[str(i)] = None

    def buildProxies(self):
        """Build the proxies for the module."""
        return super().buildProxies()
    
    def buildModule(self) -> None:
        """Run the module."""

        # Safety Check
        if self.numberOfJoints <= 0:
            cmds.error(
                f"Number of joints is less than 0 or 0; default 11: {self.numberOfJoints}")

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
        
        self.buildRibbons()

        # baseJoints, FKJoints, IKJoints, upConnector = self.buildSkeleton()
        # IKControls, FKControls, midCtrl, endCtrl, upRollJoints, loRollJoints, upIK, loIK = self.buildBaseControls(
        #     baseJoints, IKJoints, FKJoints, upConnector)
        # self.buildRibbon(baseJoints, upRollJoints,
        #                  loRollJoints, midCtrl, endCtrl)

        # # Cleanup
        # cmds.parent(baseJoints[0], self.moduleUtilities)
    def buildRibbons(self):
        relativeAxes = self.axesToVector(axis="Y")
        targets = []
        points = []
        name = f"{self.side}_{self.label}"
        for key, val in self.proxies.items():
            if key != "UpVector":
                tGrp = cmds.createNode("transform", n=f"{name}_{key}_temp")
                cmds.xform(tGrp, ws=True, t=val.position)
                targets.append(tGrp)
                points.append(val.position)
            else:
                self.upVector = cmds.createNode("transform", n=f"{name}_{key}_temp")
                cmds.xform(self.upVector, ws=True, t=val.position)
        
        jointTools.aimSequence(targets=targets, upObj=self.upVector)
        folGrp = cmds.createNode(
            "transform", n=f"{self.side}_{self.label}_follicles")
        # cmds.error("##")
        tempCurve = cmds.curve(n="TempCurve_1", d=1, p=points)
        tempCurve2 = cmds.duplicate(tempCurve, n="TempCurve_2")[0]
        cmds.parent([tempCurve, tempCurve2], targets[0])
        # print(relativeAxes)
        # cmds.error("##")
        cmds.xform(tempCurve, r=True, t=relativeAxes[0])
        cmds.xform(tempCurve2, r=True, t=relativeAxes[1])

        ribbon = cmds.loft([tempCurve2, tempCurve], n=f"{self.side}_{self.label}_Bendy_rbn", ch=False)[0]

        cmds.reverseSurface(ribbon, d=3, ch=False, rpo=1)
        cmds.rebuildSurface(
            ribbon, rpo=1, rt=0, end=1, kr=0, kcp=0, kc=0,
            su=self.spans-1, du=3, sv=1, dv=1, tol=0.01, fr=0, dir=2, ch=False
        )
        self.buildRibbonControls(ribbon=ribbon, allFollicles=folGrp)
        cmds.delete(targets)
        cmds.delete(self.upVector)
        

    def buildRibbonControls(self, ribbon, allFollicles):
        '''
        Make a meta and local ribbon, one that is bound to the skeleton, and another bound to the meta. 
        '''
        name = f"{self.side}_{self.label}"
        # Create Meta ribbon
        metaRibbon = cmds.duplicate(ribbon,
                             n=f"{self.side}_{self.label}_Meta_rbn",
                             rc=True)[0]
        shape = cmds.listRelatives(metaRibbon, c=True, s=True)[0]
        # cmds.rename(shape, "{}_{}_{}Shape_rbn".format(self.name.side, self.name.label, self.proxies["Nurbs"].name))

        metaFollicles = cmds.createNode("transform", n=f"{name}_MetaFollicles")
        regionFollicles = cmds.createNode("transform", n=f"{name}_RegionFollicles")
        mFollicles = []
        mFolJoints = []
        mFolCtrlGrps = []
        mFolCtrls = []
        rFollicles = []
        rFolJoints = []
        rFolCtrlGrps = []
        rFolCtrls = []

        # Create Meta follicles
        param = 0
        paramInfl = 1 / (self.spans - 1)
        for i in range(self.spans):

            # Build Follicles
            fol = cmds.createNode(
                "transform", n=f"{self.side}_{self.label}_{i}_fol")
            folShape = cmds.createNode(
                "follicle", n=f"{self.side}_{self.label}_{i}_folShape", p=fol)

            cmds.connectAttr(
                f"{metaRibbon}.worldMatrix[0]", f"{folShape}.inputWorldMatrix", f=True)
            cmds.connectAttr(f"{metaRibbon}.local",
                             f"{folShape}.inputSurface", f=True)
            cmds.setAttr(f"{folShape}.parameterV", 0.5)
            cmds.setAttr(f"{folShape}.parameterU", param)
            cmds.connectAttr(f"{folShape}.outRotate", f"{fol}.rotate", f=True)
            cmds.connectAttr(f"{folShape}.outTranslate",
                             f"{fol}.translate", f=True)

            cmds.parent(fol, metaFollicles)

            if param > 1:
                param = 1
            param += paramInfl

            mFollicles.append([fol, folShape])  

            # Build Joints and controls
            
            # cmds.xform(jnt, ws=True, t=cmds.xform(
            #     fol, q=True, ws=True, t=True
            # ))
            # cmds.xform(jnt, ws=True, ro=cmds.xform(
            #     fol, q=True, ws=True, ro=True
            # ))
            # cmds.parent(jnt, fol)
            # mFolJoints.append(jnt)
            grp = cmds.createNode("transform", n=f"{self.side}_{self.label}_{i}_Meta_grp", p=fol)
            ctrl = cmds.createNode("transform", n=f"{self.side}_{self.label}_{i}_Meta_CTRL", p=grp)
            jnt = cmds.createNode("joint", n=f"{self.side}_{self.label}_{i}_Meta", p=ctrl)
            ctrlObject = ctrlCrv.Ctrl(
                node=ctrl,
                shape="sphere",
                scale=[self.ctrlScale[0] * 1.125, self.ctrlScale[1] * 1.125, self.ctrlScale[2] * 1.125],
                offset=[0, 0, 0],
                orient=[0, 0, 0]
            )
            ctrlObject.giveCtrlShape()

            cmds.xform(grp, ws=True, t=cmds.xform(
                fol, q=True, ws=True, t=True
            ))

            mFolCtrlGrps.append(grp)
            mFolCtrls.append(ctrl)
            mFolJoints.append(jnt)
            self.sockets[f"Meta_{i}"] = jnt
            if len(mFolJoints) == 1:
                self.bindJoints[jnt] = None
            else:
                self.bindJoints[jnt] = mFolJoints[len(mFolJoints) - 1]

        jointTools.aimSequence(mFolCtrlGrps, upObj=self.upVector)
        mScls = cmds.skinCluster(mFolJoints, ribbon, n=f"{ribbon}_scls",
                                 sm=0, omi=True, mi=4, tsb=True)
        param = 0
        paramInfl = 1 / (self.numberOfJoints - 1)
        for i in range(self.numberOfJoints):

            # Build Follicles
            fol = cmds.createNode(
                "transform", n=f"{self.side}_{self.label}_{i}_Meta_fol")
            folShape = cmds.createNode(
                "follicle", n=f"{self.side}_{self.label}_{i}_Meta_folShape", p=fol)

            cmds.connectAttr(
                f"{ribbon}.worldMatrix[0]", f"{folShape}.inputWorldMatrix", f=True)
            cmds.connectAttr(f"{ribbon}.local",
                             f"{folShape}.inputSurface", f=True)
            cmds.setAttr(f"{folShape}.parameterV", 0.5)
            cmds.setAttr(f"{folShape}.parameterU", param)
            cmds.connectAttr(f"{folShape}.outRotate", f"{fol}.rotate", f=True)
            cmds.connectAttr(f"{folShape}.outTranslate",
                             f"{fol}.translate", f=True)

            cmds.parent(fol, regionFollicles)

            if param > 1:
                param = 1
            param += paramInfl

            rFollicles.append([fol, folShape])  

            # Joints and controls
            # grp = cmds.createNode("transform", n=f"{self.side}_{self.label}_{i}_Region_grp")
            # ctrl = cmds.createNode("transform", n=f"{self.side}_{self.label}_{i}_Region_CTRL", p=grp)
            jnt = cmds.createNode("joint", n=f"{self.side}_{self.label}_{i}", p=fol)
            # ctrlObject = ctrlCrv.Ctrl(
            #     node=ctrl,
            #     shape="circle",
            #     scale=[self.ctrlScale[0], self.ctrlScale[1], self.ctrlScale[2]],
            #     offset=[0, 0, 0],
            #     orient=[0, 90, 0]
            # )
            # ctrlObject.giveCtrlShape()

            cmds.xform(jnt, ws=True, t=cmds.xform(
                fol, q=True, ws=True, t=True
            ))

            # mFolCtrlGrps.append(grp)
            # mFolCtrls.append(ctrl)
            rFolJoints.append(jnt)
            self.sockets[f"Region_{i}"] = jnt
            if len(rFolJoints) == 1:
                self.bindJoints[jnt] = mFolJoints[0]
            else:
                self.bindJoints[jnt] = rFolJoints[len(rFolJoints) - 1]

        jointTools.aimSequence(rFolJoints, upObj=self.upVector)
        cmds.makeIdentity(rFolJoints, a=True)

        # Cleanup
        cmds.parent([ribbon, metaRibbon], self.moduleUtilities)
        cmds.parent([metaFollicles, regionFollicles], allFollicles)
        cmds.parent(allFollicles, self.moduleNode)
        self.addSocketMetaData()

        # Create Relative node
    def axesToVector(self, axis="X"):
        set = ["X", "Y", "Z"]
        if axis.upper() == set[0]:
            return [[1, 0, 0], [-1, 0, 0]]
        if axis.upper() == set[1]:
            return [[0, 1, 0], [0, -1, 0]]
        if axis.upper() == set[2]:
            return [[0, 0, 1], [0, 0, -1]]
