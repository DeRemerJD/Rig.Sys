"""FK Motion Module."""

import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import rigsys.lib.proxy as proxy
import rigsys.lib.joint as jointTools

import maya.cmds as cmds


class FK(motionBase.MotionModuleBase):
    """FK Motion Module."""

    def __init__(self, rig, side="", label="", ctrlShapes="circle", ctrlScale=None, addOffset=True, segments=5,
                 buildOrder: int = 2000, isMuted: bool = False, parent: str = None, 
                 mirror: bool = False, selectedPlug: str = "", selectedParentSocket: str = "") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, parent, mirror, selectedPlug, selectedParentSocket)
        
        self.addOffset = addOffset
        self.ctrlShapes = ctrlShapes
        self.ctrlScale = ctrlScale
        self.segments = segments

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

            self.proxies["End"].parent = str(segments-1)

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

    def buildModule(self):
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

        FKJoints = []
        # Make joints
        for key, val in self.proxies.items():
            if key != "End" or key != "UpVector":
                fJnt = cmds.createNode("joint", n=f"{self.getFullName()}_{val.name}")
                FKJoints.append(fJnt)
                cmds.xform(fJnt, ws=True, t=val.position)
        
        index = 0
        for fJnt in FKJoints:
            if fJnt != FKJoints[-1]:
                cmds.parent(FKJoints[index+1], fJnt)
            index+=1

        jointTools.aimSequence(
            FKJoints, aimAxis="+x", upAxis="-z", 
            upObj=f"{self.getFullName()}_{self.proxies['UpVector'].name}_proxy"
            )
        FKGrps = []
        FKCtrls = []
        for fJnt in FKJoints:
            grp = cmds.createNode("transform", n=f"{fJnt}_grp")
            ctrl = cmds.createNode("transform", n=f"{fJnt}_CTRL")
            cmds.parent(ctrl, grp)

            cmds.xform(grp, ws=True, t=cmds.xform(
                fJnt, q=True, ws=True, t=True
            ))
            cmds.xform(grp, ws=True, ro=cmds.xform(
                fJnt, q=True, ws=True, ro=True
            ))

            FKGrps.append(grp)
            FKCtrls.append(ctrl)

            


