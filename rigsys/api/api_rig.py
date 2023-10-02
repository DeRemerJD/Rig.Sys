"""Rig API module."""

import maya.cmds as cmds

import rigsys.modules.motion.motionBase as motionBase


class Rig:
    """Rig class."""

    def __init__(self, name: str = "Rig") -> None:
        """Initialize the rig."""
        self.name: str = name

        self.motionModules: dict[str: motionBase.MotionModuleBase] = {}
        self.deformerModules = {}
        self.utilityModules = {}
        self.exportModules = {}

    def build(self, buildLevel: int = -1) -> bool:
        """Build the rig up to the specified level.

        Args:
            buildLevel (int, optional): The level to which the rig should be built. Defaults to -1, which means all
                modules will be built.

        Returns:
            bool: True if successful, False otherwise.
        """
        success = True

        allModules: list = []
        allModules.extend(self.motionModules.values())
        allModules.extend(self.deformerModules.values())
        allModules.extend(self.utilityModules.values())
        allModules.extend(self.exportModules.values())

        allModules.sort(key=lambda x: x.buildOrder)

        for module in allModules:
            if buildLevel != -1 and module.buildOrder > buildLevel:
                break

            if not module.isMuted:
                module.run()

        return success

    def setParent(self, childModule: str, parentModule: str):
        """Set the parent of childModule to parentModule."""
        if childModule not in self.motionModules:
            raise Exception(f"Child module {childModule} does not exist.")

        if parentModule not in self.motionModules:
            raise Exception(f"Parent module {parentModule} does not exist.")

        childModule = self.motionModules[childModule]
        parentModule = self.motionModules[parentModule]
        childModule.parent = parentModule.name
        childModule._parentObject = parentModule

        # TODO: Mirroring
