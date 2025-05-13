"""World Root Motion Module."""


import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds


class PointTarget(motionBase.MotionModuleBase):
    """Root Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="sphere", ctrlScale=None,
                 buildOrder: int = 2000, isMuted: bool = False, parent: str = None, mirror: bool = False,
                 bypassProxiesOnly: bool = True, selectedPlug: str = "", selectedSocket: str = "",
                 nameSet: dict = {"Point": "Point"}, targets: list = None, constrainType: str = None,
                 effectTargets: bool = False, maintainOffset: bool = True, targetsInfluence: list = None,
                 aimAxis: str = "+x", upAxis: str = "-z") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, 
                         parent, mirror, bypassProxiesOnly, selectedPlug, 
                         selectedSocket, aimAxis, upAxis)

        if ctrlScale is None:
            ctrlScale = [1.0, 1.0, 1.0]

        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        self.nameSet = nameSet
        self.targets = targets
        self.constrainType = constrainType
        self.effectTargets = effectTargets
        self.maintainOffset = maintainOffset
        self.targetsInfluence = targetsInfluence

        self.proxies = {
            "Point": proxy.Proxy(
                position=[0, 0, 0],
                rotation=[0, 0, 0],
                side=self.side,
                label=self.label,
                name=self.nameSet["Point"],
            )
        }

        self.sockets = {
            "Point": None
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

        # Get Proxy pos / rot values
        proxyPosition = self.proxies["Point"].position
        proxyRotation = self.proxies["Point"].rotation

        # MAKE MODULE NODES
        self.moduleHierarchy()

        # Make Plug Transforms
        self.plugParent = self.createPlugParent(
            position=proxyPosition, rotation=proxyRotation
        )
        self.worldParent = self.createWorldParent()
        self.plugs["Local"] = self.plugParent
        self.plugs["World"] = self.worldParent

        # Structure
        rootPar = cmds.createNode("transform", n=self.getFullName() + "_grp")
        rootCtrl = cmds.createNode("transform", n=self.getFullName() + "_CTRL")
        cmds.parent(rootCtrl, rootPar)
        rootCtrlObj = ctrlCrv.Ctrl(
            node=rootCtrl,
            shape=self.ctrlShapes,
            scale=self.ctrlScale,
            orient=[0, 0, 0],
        )
        rootCtrlObj.giveCtrlShape()
        rootJnt = cmds.createNode(
            "joint", n="{}_{}_{}".format(self.side, self.label, self.proxies["Point"].name)
        )
        cmds.setAttr(f"{rootJnt}.drawStyle", 2)
        cmds.setAttr(f"{rootCtrl}.visibility", l=True, k=False)
        cmds.parent(rootJnt, rootCtrl)
        self.sockets["Point"] = rootJnt
        self.bindJoints[rootJnt] = None
       
        cmds.xform(rootPar, ws=True, t=proxyPosition)
        cmds.xform(rootPar, ws=True, ro=proxyRotation)
        if self.parent == "" or self.parent is None:
            cmds.parent(rootPar, self.worldParent)
        else:
            cmds.parent(rootPar, self.plugParent)

        if self.targets is not None:
            if isinstance(self.targets, str):
                if cmds.objExists(self.targets):
                    self.targets = [self.targets]
                else:
                    cmds.error(f"Targets: {self.targets}, does not exist.")
            elif isinstance(self.targets, list):
                doesNotExist = []
                for i in self.targets:
                    if cmds.objExists(i):
                        pass
                    else:
                        doesNotExist.append(i)
                if len(doesNotExist) > 0:
                    cmds.error(f"Targets: {doesNotExist}, do not exist.")
            else:
                cmds.error(f"Targets: {self.targets}, not str or list.")

            if self.side == "L":
                index = 0
                for i in self.targets:
                    if i.startswith("R_"):
                        oldName = i.split("_")
                        oldName[0] = "L"
                        newName = "_".join(oldName)
                        self.targets[index] = newName
                    index+=1

            elif self.side == "R":
                index = 0
                for i in self.targets:
                    if i.startswith("L_"):
                        oldName = i.split("_")
                        oldName[0] = "R"
                        newName = "_".join(oldName)
                        self.targets[index] = newName
                    index+=1

            allowedConstraints = ["parent", "point", "orient", "aim", "scale"]
            if self.constrainType not in allowedConstraints:
                cmds.error(f"constraint Type: '{self.constrainType}' not permitted, try {allowedConstraints}")
            
            if self.effectTargets:
                if self.constrainType == "parent":
                    for i in self.targets:
                        nPar = cmds.createNode("transform", n=f"{i}_{self.label}Offset")
                        cmds.xform(nPar, ws=True, m=cmds.xform(
                            i, q=True, ws=True, m=True
                        ))
                        iPar = cmds.listRelatives(i, p=True)[0]
                        cmds.parent(nPar, iPar)
                        cmds.parent(i, nPar)
                        ptc = cmds.parentConstraint(rootCtrl, nPar, n=f"{nPar}_PTC", mo=self.maintainOffset)[0]
                        cmds.setAttr(f"{ptc}.interpType", 2)
                    if len(self.targetsInfluence) == len(self.targets):
                        index = 0
                        for i in self.targets:
                            cmds.setAttr(f"{ptc}.{i}W{index}", self.targetsInfluence[index])
                            index+=1
                elif self.constrainType == "point":
                    for i in self.targets:
                        nPar = cmds.createNode("transform", n=f"{i}_{self.label}Offset")
                        cmds.xform(nPar, ws=True, m=cmds.xform(
                            i, q=True, ws=True, m=True
                        ))
                        iPar = cmds.listRelatives(i, p=True)[0]
                        cmds.parent(nPar, iPar)
                        cmds.parent(i, nPar)
                        pc = cmds.pointConstraint(rootCtrl, nPar, n=f"{rootPar}_PC", mo=self.maintainOffset)[0]
                    if len(self.targetsInfluence) == len(self.targets):
                        index = 0
                        for i in self.targets:
                            cmds.setAttr(f"{pc}.{i}W{index}", self.targetsInfluence[index])
                            index+=1
                elif self.constrainType == "orient":
                    for i in self.targets:
                        nPar = cmds.createNode("transform", n=f"{i}_{self.label}Offset")
                        cmds.xform(nPar, ws=True, m=cmds.xform(
                            i, q=True, ws=True, m=True
                        ))
                        iPar = cmds.listRelatives(i, p=True)[0]
                        cmds.parent(nPar, iPar)
                        cmds.parent(i, nPar)
                        oc = cmds.parentConstraint(rootCtrl, nPar, n=f"{rootPar}_OC", mo=self.maintainOffset)
                        cmds.setAttr(f"{oc}.interpType", 2)
                    if len(self.targetsInfluence) == len(self.targets):
                        index = 0
                        for i in self.targets:
                            cmds.setAttr(f"{oc}.{i}W{index}", self.targetsInfluence[index])
                            index+=1
                elif self.constrainType == "aim":
                    for i in self.targets:
                        nPar = cmds.createNode("transform", n=f"{i}_{self.label}Offset")
                        cmds.xform(nPar, ws=True, m=cmds.xform(
                            i, q=True, ws=True, m=True
                        ))
                        iPar = cmds.listRelatives(i, p=True)[0]
                        cmds.parent(nPar, iPar)
                        cmds.parent(i, nPar)
                        aim = jointTools.axisToVector(self.aimAxis)
                        up = jointTools.axisToVector(self.upAxis)
                        aim = cmds.aimConstraint(rootCtrl, nPar, n=f"{rootPar}_AC", mo=self.maintainOffset,
                                                aim=aim, u=up, wut="objectrotation", wuo=rootCtrl)[0]
                    if len(self.targetsInfluence) == len(self.targets):
                        index = 0
                        for i in self.targets:
                            cmds.setAttr(f"{aim}.{rootCtrl}W{index}", self.targetsInfluence[index])
                            index+=1
                else:
                    for i in self.targets:
                        nPar = cmds.createNode("transform", n=f"{i}_{self.label}Offset")
                        cmds.xform(nPar, ws=True, m=cmds.xform(
                            i, q=True, ws=True, m=True
                        ))
                        iPar = cmds.listRelatives(i, p=True)[0]
                        cmds.parent(nPar, iPar)
                        cmds.parent(i, nPar)
                        sc = cmds.scaleConstraint(rootCtrl, nPar, n=f"{rootPar}_SC", mo=self.maintainOffset)[0]
                    if len(self.targetsInfluence) == len(self.targets):
                        index = 0
                        for i in self.targets:
                            cmds.setAttr(f"{sc}.{i}W{index}", self.targetsInfluence[index])
                            index+=1
            else:
                if self.constrainType == "parent":
                    ptc = cmds.parentConstraint(self.targets, rootPar, n=f"{rootPar}_PTC", mo=self.maintainOffset)[0]
                    cmds.setAttr(f"{ptc}.interpType", 2)
                    if len(self.targetsInfluence) == len(self.targets):
                        index = 0
                        for i in self.targets:
                            cmds.setAttr(f"{ptc}.{i}W{index}", self.targetsInfluence[index])
                            index+=1
                elif self.constrainType == "point":
                    pc = cmds.pointConstraint(self.targets, rootPar, n=f"{rootPar}_PC", mo=self.maintainOffset)[0]
                    if len(self.targetsInfluence) == len(self.targets):
                        index = 0
                        for i in self.targets:
                            cmds.setAttr(f"{pc}.{i}W{index}", self.targetsInfluence[index])
                            index+=1
                elif self.constrainType == "orient":
                    oc = cmds.parentConstraint(self.targets, rootPar, n=f"{rootPar}_OC", mo=self.maintainOffset)[0]
                    cmds.setAttr(f"{oc}.interpType", 2)
                    if len(self.targetsInfluence) == len(self.targets):
                        index = 0
                        for i in self.targets:
                            cmds.setAttr(f"{oc}.{i}W{index}", self.targetsInfluence[index])
                            index+=1
                elif self.constrainType == "aim":
                    aim = jointTools.axisToVector(self.aimAxis)
                    up = jointTools.axisToVector(self.upAxis)
                    aim = cmds.aimConstraint(self.targets, rootPar, n=f"{rootPar}_AC", mo=self.maintainOffset,
                                            aim=aim, up=up, wut="objectrotation", wuo=rootCtrl)[0]
                    if len(self.targetsInfluence) == len(self.targets):
                        index = 0
                        for i in self.targets:
                            cmds.setAttr(f"{aim}.{i}W{index}", self.targetsInfluence[index])
                            index+=1
                else:
                    sc = cmds.scaleConstraint(self.targets, rootPar, n=f"{rootPar}_SC", mo=self.maintainOffset)[0]
                    if len(self.targetsInfluence) == len(self.targets):
                        index = 0
                        for i in self.targets:
                            cmds.setAttr(f"{sc}.{i}W{index}", self.targetsInfluence[index])
                            index+=1
        self.addSocketMetaData()
