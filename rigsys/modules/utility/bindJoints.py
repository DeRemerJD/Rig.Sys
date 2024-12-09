"""Build bind joints utility module."""

import logging
import rigsys.modules.utility.utilityBase as utilityBase
import maya.cmds as cmds

logger = logging.getLogger(__name__)


class BindJoints(utilityBase.UtilityModuleBase):
    """Build bind joints utility module."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 3000, isMuted: bool = False,
                 mirror: bool = False, bypassProxiesOnly: bool = False, underGroup: str = "") -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, mirror, bypassProxiesOnly)
        self.underGroup = underGroup

    def run(self) -> None:
        """Run the module."""
        # TODO: Implement
        motionModules = list(self._rig.motionModules.values())

        for module in motionModules:
            # if not module.isRun:
            #     logger.error(f"Module not run: {module.getFullName()}. Unable to perform parenting.")
            #     continue

            for jnt in module.bindJoints.keys():
                bindJoint = cmds.createNode("joint", n=f"{jnt}_bind")
                cmds.xform(bindJoint, ws=True, m=cmds.xform(
                    jnt, q=True, ws=True, m=True
                ))
                cmds.makeIdentity(bindJoint, a=True)
                if bindJoint.startswith("L_"):
                    side = 1
                    jlabel = "_".join(bindJoint.split("_")[1:])
                elif bindJoint.startswith("R_"):
                    side = 2
                    jlabel = "_".join(bindJoint.split("_")[1:])
                elif bindJoint.startswith("M_"):
                    side = 0
                    jlabel = "_".join(bindJoint.split("_")[1:])
                else:
                    side = 3
                    jlabel = "_".join(bindJoint.split("_")[1:])
                cmds.setAttr(f"{bindJoint}.side", side)
                cmds.setAttr(f"{bindJoint}.type", 18)
                cmds.setAttr(f"{bindJoint}.otherType", jlabel, type="string")

            for jnt, parJnt in module.bindJoints.items():
                if parJnt is None:
                    pass
                else:
                    cmds.parent(f"{jnt}_bind", f"{parJnt}_bind")

        floatingJoints = []
        for module in motionModules:
            # if not module.isRun:
            #     logger.error(f"Module not run: {module.getFullName()}. Unable to perform parenting.")
            #     continue
            # Get other modules socket bind joint.
            if module.parent is not None:
                for jnt, parJnt in module.bindJoints.items():
                    if parJnt is None:
                        # Check if bind exists
                        print(f" CURRENT: {module.side}_{module.label} PARENTING TO: {module.parent}_MODULE.{module.selectedSocket}")
                        constructedBind = cmds.getAttr(f"{module.parent}_MODULE.{module.selectedSocket}", asString=True)
                        constructedBind = f"{constructedBind}_bind"
                        if cmds.objExists(constructedBind):
                            cmds.parent(f"{jnt}_bind", f"{constructedBind}")
            else:
                if self.underGroup is not None or self.underGroup != "":

                    if cmds.objExists(self.underGroup):

                        for jnt, parJnt in module.bindJoints.items():
                            if parJnt is None:
                                floatingJoints.append(f"{jnt}_bind")
        cmds.parent(floatingJoints, self.underGroup)

        for module in motionModules:
            for jnt in module.bindJoints.keys():
                cmds.parentConstraint(jnt, f"{jnt}_bind", mo=0, n=f"{jnt}_bind_ptc")
                cmds.scaleConstraint(jnt, f"{jnt}_bind", mo=0, n=f"{jnt}_bind_sc")
