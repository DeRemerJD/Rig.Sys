"""Build bind joints utility module."""

import logging
import rigsys.modules.utility.utilityBase as utilityBase
import maya.cmds as cmds

logger = logging.getLogger(__name__)

class BindJoints(utilityBase.UtilityModuleBase):
    """Build bind joints utility module."""

    def __init__(self, rig, label: str = "", buildOrder: int = 3000, isMuted: bool = False,
                 mirror: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig, label, buildOrder, isMuted, mirror)

    def run(self) -> None:
        """Run the module."""
        # TODO: Implement
        motionModules = list(self._rig.motionModules.values())
        print("############")
        # cmds.error("##")
        for module in motionModules:
            # if not module.isRun:
            #     logger.error(f"Module not run: {module.getFullName()}. Unable to perform parenting.")
            #     continue            

            for jnt in module.bindJoints.keys():
                print(jnt)
                bindJoint = cmds.createNode("joint", n=f"{jnt}_bind")
                cmds.xform(bindJoint, ws=True, m=cmds.xform(
                    jnt, q=True, ws=True, m=True
                ))
                cmds.makeIdentity(bindJoint, a=True)
            for jnt, parJnt in module.bindJoints.items():
                if parJnt is None:
                    pass
                else:
                    cmds.parent(f"{jnt}_bind", f"{parJnt}_bind")
        
        for module in motionModules:
            # if not module.isRun:
            #     logger.error(f"Module not run: {module.getFullName()}. Unable to perform parenting.")
            #     continue
            # Get other modules socket bind joint.
            for jnt, parJnt in module.bindJoints.items():
                if parJnt is None:
                    # Check if bind exists
                    constructedBind = cmds.getAttr(f"{module.parent}_MODULE.{module.selectedSocket}", asString=True)
                    constructedBind = f"{constructedBind}_bind"
                    if cmds.objExists(constructedBind):
                        cmds.parent(f"{jnt}_bind", f"{constructedBind}")
            # if module.parent is None or module.parent == "":
            #     continue

            # if module.selectedSocket not in module._parentObject.sockets:
            #     logger.error(f"Parent socket not found: {module.selectedSocket}")
            #     continue

            # if module.selectedPlug is None or module.selectedPlug == "":
            #     module.selectedPlug = "Local"

            # plugNode = module.plugs[module.selectedPlug]
            # socketNode = module._parentObject.sockets[module.selectedSocket]
            # logger.info(f"Parenting {module.getFullName()} at {plugNode} to {module.parent} at {socketNode}")
            # # TODO: Jacob, do the actual parenting here
            # module.socketPlugParenting()
