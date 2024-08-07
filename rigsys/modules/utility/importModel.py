"""Import model utility module."""

import logging
import os

import rigsys.modules.utility.utilityBase as utilityBase

import maya.cmds as cmds


logger = logging.getLogger(__name__)


class ImportModel(utilityBase.UtilityModuleBase):
    """Import model utility module."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 3000, isMuted: bool = False,
                 mirror: bool = False, bypassProxiesOnly: bool = True, 
                 filePath: str = "", underGroup: str = None) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, mirror, bypassProxiesOnly)
        self.side = 'M'
        self.filePath = filePath
        self.underGroup = underGroup

    def run(self) -> None:
        """Run the module."""
        if not os.path.exists(self.filePath):
            raise ValueError(f"File does not exist: {self.filePath}")

        filePathLowercase = self.filePath.lower()
        if filePathLowercase.endswith(".ma"):
            fileType = "mayaAscii"
        elif filePathLowercase.endswith(".mb"):
            fileType = "mayaBinary"
        elif filePathLowercase.endswith(".obj"):
            fileType = "OBJexport"
        elif filePathLowercase.endswith(".fbx"):
            fileType = "FBX"
        else:
            raise ValueError(f"File type not supported: {self.filePath}")

        newNodes = cmds.file(self.filePath, i=True, rnn=True, type=fileType)

        rootNodes = []
        for node in newNodes:
            if not cmds.objExists(node):
                logger.warning(f"node does not exist: {node}")
                continue

            parent = cmds.listRelatives(node, p=True)
            if not parent:
                nodeTypes = cmds.nodeType(node, i=True)
                if "dagNode" in nodeTypes:
                    rootNodes.append(node)

        if self.underGroup is None or self.underGroup == "":
            underGroup = self._rig.rigNode
        else:
            underGroup = self.underGroup

            if not cmds.objExists(self.underGroup):
                underGroup = cmds.createNode("transform", n=self.underGroup)
                cmds.parent(underGroup, self._rig.rigNode)

        for node in rootNodes:
            logger.info(f"Parenting {node} under {underGroup}")
            cmds.parent(node, underGroup)
