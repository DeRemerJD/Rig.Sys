"""Example character to showcase the rigsys module."""

import rigsys.utils.unload as unload

unload.unloadPackages(silent=True, packages=["rigsys"])

import rigsys.api.api_rig as api_rig
import rigsys.modules.utility as utility

import maya.cmds as cmds
cmds.file(new=True, force=True)


class ExampleCharacter(api_rig.Rig):
    """Example character to showcase the rigsys module."""

    def __init__(self, name: str = "ExampleRig") -> None:
        """Initialize the Rig."""
        super().__init__(name)

        self.motionModules = {}
        self.deformerModules = {}
        self.utilityModules = {
            "ImportModel": utility.ImportModel(
                self,
                filePath=r"C:\Users\gabri\Documents\GitHub\Rig.Sys\example\cube.mb",
                underGroup=""
            ),
        }
        self.exportModules = {}


if __name__ == "__main__":
    character = ExampleCharacter()
    character.build()
