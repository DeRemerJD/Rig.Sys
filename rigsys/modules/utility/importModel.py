"""Import model utility module."""


import rigsys.modules.utility.utilityBase as utilityBase

import maya.cmds as cmds


class ImportModel(utilityBase.UtilityModuleBase):
    """Import model utility module."""

    def __init__(self, filePath: str, underGroup: str = None) -> None:
        """Initialize the module."""
        super().__init__()

        self.filePath = filePath
        self.underGroup = underGroup

    def run(self) -> None:
        """Run the module."""
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
            parent = cmds.listRelatives(node, p=True)
            if not parent:
                nodeTypes = cmds.nodeType(node, i=True)
                if "dagNode" in nodeTypes:
                    rootNodes.append(node)

        if self.underGroup is None:
            return

        if not cmds.objExists(self.underGroup):
            cmds.group(n=self.underGroup, em=True)
            # TODO: This should be parented under the rig node

        for node in rootNodes:
            cmds.parent(node, self.underGroup)
