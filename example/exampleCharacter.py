"""Example character to showcase the rigsys module."""

import rigsys.utils.unload as unload

unload.unloadPackages(silent=True, packages=["rigsys"])

import os

import rigsys as rigsys
import rigsys.api.api_rig as api_rig
import rigsys.modules.utility as utility
import rigsys.modules.export as export

import maya.cmds as cmds
cmds.file(new=True, force=True)


class ExampleCharacter(api_rig.Rig):
    """Example character to showcase the rigsys module."""

    def __init__(self, name: str = "ExampleRig") -> None:
        """Initialize the Rig."""
        super().__init__(name)

        self.exampleCharacterFolder = os.path.abspath(os.path.join(rigsys.__file__, os.pardir, os.pardir, "example"))
        print(f"self.exampleCharacterFolder: {self.exampleCharacterFolder}")
        print(os.path.exists(self.exampleCharacterFolder))

        self.motionModules = {}
        self.deformerModules = {}
        self.utilityModules = {
            "ImportModel": utility.ImportModel(
                self,
                filePath=os.path.join(self.exampleCharacterFolder, "cube.mb"),
                underGroup=""
            ),
        }
        self.exportModules = {
            "FBXExport": export.FBXExport(
                self,
                exportPath=os.path.join(self.exampleCharacterFolder, "ExampleRig_export.fbx"),
                exportAll=True,
                exportSelected=False,
                nodesToExport=None,
            ),
        }


if __name__ == "__main__":
    character = ExampleCharacter()
    character.build()
