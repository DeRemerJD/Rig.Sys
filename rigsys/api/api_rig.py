"""Rig API module."""

import json
import logging
import os

import maya.cmds as cmds

import rigsys.modules.motion as motion
import rigsys.modules.utility as utility
import rigsys.modules.deformer as deformer

logger = logging.getLogger(__name__)


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
        self.motionNodes = None
        self.geometryNodes = None
        self.skeletonNodes = None
        self.deformerNodes = None
        self.utilityNodes = None
        self.proxyNodes = None

    def preBuild(self) -> list:
        """Run any pre-build steps.

        Returns:
            list: A list of all modules that need to be built.
        """
        # Add a motionModuleParenting module if one doesn't already exist
        motionModuleParentingAdded = any(
            isinstance(module, utility.MotionModuleParenting) for module in self.utilityModules.values()
        )

        if not motionModuleParentingAdded:
            self.utilityModules["MotionModuleParenting"] = utility.MotionModuleParenting(self)

        allModules: list = []
        allModules.extend(self.motionModules.values())
        allModules.extend(self.deformerModules.values())
        allModules.extend(self.utilityModules.values())
        allModules.extend(self.exportModules.values())

        # Mirroring - motion modules
        newMotionModules = []
        for module in self.motionModules.values():
            if module.mirror:
                mirroredModule = module.doMirror()
                if mirroredModule is not None:
                    newMotionModules.append(mirroredModule)

        for module in newMotionModules:
            self.motionModules[module.getFullName()] = module
            allModules.append(module)

        # Mirroring - utility modules
        newUtilityModules = []
        for module in self.utilityModules.values():
            if module.mirror:
                mirroredModule = module.doMirror()
                if mirroredModule is not None:
                    newUtilityModules.append(mirroredModule)

        for module in newUtilityModules:
            self.utilityModules[module.getFullName()] = module
            allModules.append(module)

        # Parenting
        for module in self.motionModules.values():
            if module.parent is not None:
                self.setParent(module.getFullName(), module.parent)

        # Sort by build order
        allModules.sort(key=lambda x: x.buildOrder)
        
        return allModules

    def build(self, buildLevel: int = -1, buildProxiesOnly: bool = False, usedSavedProxyData: bool = False,
              proxyDataFile: str = "") -> bool:
        """Build the rig up to the specified level.

        Args:
            buildLevel (int, optional): The level to which the rig should be built. Defaults to -1, which means all
                modules will be built.
            buildProxiesOnly (bool, optional): If True, only the proxies will be built. Defaults to False.
            useSavedProxyData (bool, optional): If True, the proxy data will be loaded from a file. Defaults to True.
            proxyDataFile (str, optional): The file to load the proxy data from. Defaults to "".

        Returns:
            bool: True if successful, False otherwise.
        """
        success = True

        proxyData = None

        if usedSavedProxyData:
            if proxyDataFile == "":
                raise Exception("No proxy data file specified.")
            elif not os.path.exists(proxyDataFile):
                raise Exception(f"Proxy data file {proxyDataFile} does not exist.")
            else:
                with open(proxyDataFile, "r") as file:
                    proxyData = json.load(file)

        cmds.file(new=True, force=True)

        # Create a group node for the rig
        if not cmds.objExists(self.name):
            self.rigNode = cmds.createNode("transform", n=self.name)
            self.buildRigHierarchy()
        else:
            self.rigNode = self.name

        allModules = self.preBuild()

        for module in allModules:
            if buildLevel != -1 and module.buildOrder > buildLevel:
                break

            if module.isMuted:
                continue

            logger.info(f"Building module {module.getFullName()}...")

            if isinstance(module, motion.MotionModuleBase):
                module.run(buildProxiesOnly=buildProxiesOnly, usedSavedProxyData=usedSavedProxyData,
                           proxyData=proxyData)

            else:
                module.run()

            module.isRun = True

            logger.info(f"Module {module.getFullName()} built.")

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
        childModule.parent = parentModule.getFullName()
        childModule._parentObject = parentModule

    def buildRigHierarchy(self):
        """Build the rig hierarchy."""
        self.motionNodes = cmds.createNode("transform", n="modules")
        self.geometryNodes = cmds.createNode("transform", n="geometry")
        self.skeletonNodes = cmds.createNode("transform", n="skeleton")
        self.deformerNodes = cmds.createNode("transform", n="deformers")
        self.utilityNodes = cmds.createNode("transform", n="utilities")
        self.proxyNodes = cmds.createNode("transform", n="proxies")

        coreNodes = [self.motionNodes, self.geometryNodes,
                     self.skeletonNodes, self.deformerNodes,
                     self.utilityNodes, self.proxyNodes]

        cmds.parent(coreNodes, self.rigNode)

    def saveProxyTransformations(self, fileName):
        """Save proxy transformations to a given file."""
        proxyData = {}

        # Ensure we get proxies from mirrored modules as well
        self.preBuild()

        for module in self.motionModules.values():
            proxyData[module.getFullName()] = {}

            for proxyKey, proxy in module.proxies.items():
                sceneName = f"{proxy.side}_{proxy.label}_{proxy.name}_proxy"
                if not cmds.objExists(sceneName):
                    logger.warning(f"Proxy {sceneName} does not exist.")
                    continue

                proxyPosition = cmds.xform(sceneName, query=True, ws=True, translation=True)
                proxyRotation = cmds.xform(sceneName, query=True, ws=True, rotation=True)

                proxyData[module.getFullName()][proxyKey] = {
                    "position": proxyPosition,
                    "rotation": proxyRotation,
                }

        with open(fileName, "w") as file:
            json.dump(proxyData, file, indent=4)
