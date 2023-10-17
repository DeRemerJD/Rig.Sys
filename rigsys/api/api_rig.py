"""Rig API module."""

import maya.cmds as cmds

import rigsys.modules.motion as motion
import rigsys.modules.deformer as deformer
import rigsys.modules.utility as utility
import rigsys.modules.export as export


class Rig:
    """Rig class."""

    def __init__(self, name: str = "Rig") -> None:
        """Initialize the rig."""
        self.name: str = name

        self.motionModules = {}
        self.deformerModules = {}
        self.utilityModules = {}
        self.exportModules = {}

        self.rigNode = None

    def build(self, buildLevel: int = -1, buildProxiesOnly: bool = False) -> bool:
        """Build the rig up to the specified level.

        Args:
            buildLevel (int, optional): The level to which the rig should be built. Defaults to -1, which means all
                modules will be built.
            buildProxiesOnly (bool, optional): If True, only the proxies will be built. Defaults to False.

        Returns:
            bool: True if successful, False otherwise.
        """
        success = True

        # Create a group node for the rig
        if not cmds.objExists(self.name):
            self.rigNode = cmds.group(n=self.name, em=True)
        else:
            self.rigNode = self.name

        allModules: list = []
        allModules.extend(self.motionModules.values())
        allModules.extend(self.deformerModules.values())
        allModules.extend(self.utilityModules.values())
        allModules.extend(self.exportModules.values())

        allModules.sort(key=lambda x: x.buildOrder)

        for module in allModules:
            if buildLevel != -1 and module.buildOrder > buildLevel:
                break

            if module.isMuted:
                continue

            if isinstance(module, motion.MotionModuleBase):
                module.run(buildProxiesOnly=buildProxiesOnly)
            else:
                module.run()

        # TODO: Do something with the success variable
        return success

    def setParent(self, childModuleName: str, parentModuleName: str):
        """Set the parent of childModule to parentModule."""
        if childModuleName not in self.motionModules:
            raise Exception(f"Child module {childModuleName} does not exist.")

        if parentModuleName not in self.motionModules:
            raise Exception(f"Parent module {parentModuleName} does not exist.")

        childModule = self.motionModules[childModuleName]
        parentModule = self.motionModules[parentModuleName]
        childModule.parent = parentModule.name
        childModule._parentObject = parentModule

        # TODO: Mirroring

    def addMotionModule(self, moduleType, moduleName=""):
        """Add a motion module to the rig."""
        if moduleType not in motion.moduleTypes:
            raise Exception(f"Motion module type {moduleType} does not exist.")

        if moduleName == "":
            moduleName = moduleType

        if moduleName in self.motionModules:
            raise Exception(f"Motion module {moduleName} already exists.")

        moduleClass = motion.moduleTypes[moduleType]
        module = moduleClass(self, moduleName)
        self.motionModules[moduleName] = module

        # TODO: Sides, mirroring

        return module
