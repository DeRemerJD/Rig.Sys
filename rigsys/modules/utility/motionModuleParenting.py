"""Motion module parenting utility module."""

import logging

import maya.cmds as cmds

from rigsys.modules.utility.utilityBase import UtilityModuleBase


logger = logging.getLogger(__name__)


class MotionModuleParenting(UtilityModuleBase):
    """Motion module parenting utility module."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 3000, isMuted: bool = False,
                 mirror: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, mirror)

    def run(self) -> None:
        """Run the module."""
        motionModules = list(self._rig.motionModules.values())

        for module in motionModules:
            if not module.isRun:
                logger.error(f"Module not run: {module.getFullName()}. Unable to perform parenting.")
                continue

            if module.parent is None or module.parent == "":
                continue

            if module.selectedSocket not in module._parentObject.sockets:
                logger.error(f"Parent socket not found: {module.selectedSocket}")
                continue

            if module.selectedPlug is None or module.selectedPlug == "":
                module.selectedPlug = "Local"

            plugNode = module.plugs[module.selectedPlug]
            socketNode = module._parentObject.sockets[module.selectedSocket]
            logger.info(f"Parenting {module.getFullName()} at {plugNode} to {module.parent} at {socketNode}")
            # TODO: Jacob, do the actual parenting here
            module.socketPlugParenting()
