"""Build bind joints utility module."""

import logging
import rigsys.modules.utility.utilityBase as utilityBase
import maya.cmds as cmds
import os as os
import json as json


logger = logging.getLogger(__name__)

class ControlShapeOverride(utilityBase.UtilityModuleBase):
    """Build bind joints utility module."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 3000, isMuted: bool = False,
                 mirror: bool = False, bypassProxiesOnly: bool = False, underGroup: str = "",
                 path: str = "", controlTargets: list = [], write: bool = False, read: bool = False) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, mirror, bypassProxiesOnly)
        self.underGroup = underGroup

        self.path = path
        self.controlTargets = controlTargets
        self.write = write
        self.read = read

    def run(self) -> None:
        """Run the module."""
        missing = []

        for obj in self.controlTargets:
            if not cmds.objExists(obj):
                missing.append(obj)

        if len(missing) > 0:
            cmds.error(f"The following controls are missing {missing}")
        
        if self.write:
            controlVertexPosition = {}
            for obj in self.controlTargets:
                shapeCheck = cmds.listRelatives(obj, s=True)
                if len(shapeCheck) > 1:
                    for shape in shapeCheck:
                        cvEnum =  cmds.getAttr(f"{shape}.cv[*]")
                        for i in range(len(cvEnum)):
                            controlVertexPosition[f"{shape}.cv[{i}]"] = cmds.pointPosition(f"{shape}.cv[{i}]", w=True)
                else:
                    cvEnum = cmds.getAttr(f"{obj}.cv[*]")
                    for i in range(len(cvEnum)):
                        controlVertexPosition[f"{obj}.cv[{i}]"] = cmds.pointPosition(f"{obj}.cv[{i}]", w=True)
            if self.path == "":
                raise Exception("No proxy data file specified.")
            elif not os.path.exists(self.path):
                raise Exception(f"Proxy data file {self.path} does not exist.")
            else:
                with open(self.path, "w") as file:
                    json.dump(controlVertexPosition, file, indent=4)
        if self.read:
            if self.path == "":
                raise Exception("No proxy data file specified.")
            elif not os.path.exists(self.path):
                raise Exception(f"Proxy data file {self.path} does not exist.")
            else:
                with open(self.path, "r") as file:
                    controlVertexPosition = json.load(file)
                for vert, pos in controlVertexPosition.items():
                    cmds.xform(vert, ws=True, t=pos)
