"""Build bind joints utility module."""

import logging
import rigsys.modules.utility.utilityBase as utilityBase
import maya.cmds as cmds

logger = logging.getLogger(__name__)

class SpaceSwitch(utilityBase.UtilityModuleBase):
    """Build bind joints utility module."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 3000, isMuted: bool = False,
                 mirror: bool = False, bypassProxiesOnly: bool = False, underGroup: str = "",
                 constrainedTarget: str = "", switchTargets: list = []) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, mirror, bypassProxiesOnly)
        self.underGroup = underGroup

        self.constrainedTarget = constrainedTarget
        self.switchTargets = switchTargets

    def run(self) -> None:
        """Run the module."""
        # TODO: Implement
        motionModules = list(self._rig.motionModules.values())

        for module in motionModules:
            pass

        # checks
        if self.constrainedTarget == "":
            cmds.error("Constrained targets is empty.")
        if not cmds.objExists(self.constrainedTarget):
            cmds.error(f"Constrained Target: {self.constrainedTarget} does not exist.")
        if len(self.switchTargets) == 0:
            cmds.error("Space Switch list of targets empty.")
        missing = []
        for i in self.switchTargets:
            if not cmds.objExists(i):
                missing.append(i)
        if len(missing) > 0:
            cmds.error(f"The following switch targets do not exist: {missing}")

        #Actual code now...
        cmds.addAttr(self.constrainedTarget, ln="DynParent", 
                     at="enum", en="------", keyable=1)
        cmds.setAttr(f"{self.constrainedTarget}.DynParent", l=True)

        originalParent = cmds.listRelatives(self.constrainedTarget, p=True)
        if originalParent is not None:
            originalParent = originalParent[0]
        dynOffset = cmds.createNode("transform", 
                                    n=f"{self.constrainedTarget}_dynOffset")
        dynSelf = cmds.createNode("transform",
                                  n=f"{self.constrainedTarget}_dynSelf")
        cmds.parent(dynOffset, dynSelf)
        cmds.xform(dynSelf, ws=True, t=cmds.xform(
            originalParent, q=True, ws=True, t=True
        ))
        cmds.xform(dynSelf, ws=True, ro=cmds.xform(
            originalParent, q=True, ws=True, ro=True
        ))
        cmds.parent(dynSelf, originalParent)
        cmds.parent(self.constrainedTarget, dynOffset)
        updatedSwitchTargets = [dynSelf]
        updatedSwitchTargets.extend(self.switchTargets)
        enumString = "self:"
        for i in updatedSwitchTargets:
            if i != updatedSwitchTargets[0]:
                enumString += f"{i}:"
        
        ptc = cmds.parentConstraint(updatedSwitchTargets, dynOffset,
                                    n=f"{originalParent}_dynParent_ptc", mo=0)[0]
        cmds.addAttr(self.constrainedTarget, ln="switchTargets", 
                     at="enum", en=enumString, keyable=1)
        for index, obj in enumerate(updatedSwitchTargets):
            cnd = cmds.createNode("condition", n=f"{obj}_dynChoice")
            cmds.connectAttr(f"{self.constrainedTarget}.switchTargets", f"{cnd}.firstTerm")
            cmds.setAttr(f"{cnd}.secondTerm", index)
            cmds.setAttr(f"{cnd}.colorIfTrueR", 1)
            cmds.setAttr(f"{cnd}.colorIfFalseR", 0)
            cmds.connectAttr(f"{cnd}.outColorR", f"{ptc}.{obj}W{index}")
            # if index == 0:
            #     cmds.addAttr(self.constrainedTarget, ln="self", at="long",
            #              min=0, max=1, dv=1, k=True)
            #     cmds.connectAttr(f"{self.constrainedTarget}.self", f"{ptc}.{obj}W{index}")
            # else:
            #     cmds.addAttr(self.constrainedTarget, ln=obj, at="long",
            #              min=0, max=1, dv=0, k=True)
            #     cmds.connectAttr(f"{self.constrainedTarget}.{obj}", f"{ptc}.{obj}W{index}")
        print(f"Space Switch for {self.constrainedTarget} Complete. . .")