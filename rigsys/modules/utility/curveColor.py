"""Build bind joints utility module."""

import logging
import rigsys.modules.utility.utilityBase as utilityBase
import maya.cmds as cmds

logger = logging.getLogger(__name__)

class RGBCurveColor(utilityBase.UtilityModuleBase):
    """Build bind joints utility module."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 3000, isMuted: bool = False,
                 mirror: bool = False, bypassProxiesOnly: bool = False, underGroup: str = "",
                 colorOverride: dict = {}) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, mirror, bypassProxiesOnly)
        self.underGroup = underGroup

        self.colorOverride = colorOverride

    def run(self) -> None:
        """Run the module."""
        # TODO: Implement
        motionModules = list(self._rig.motionModules.values())

        for module in motionModules:
            pass

        colorKeys = {
            "red": [1.00, 0.00, 0.00],
            "green": [0.00, 1.00, 0.00],
            "blue": [0.00, 0.00, 1.00],            
            "yellow": [1.00, 1.00, 0.00],
            "pink": [2.32, 0.60, 0.57],
            "sage": [0.21, 0.45, 0.20],
            "teal": [0.22, 0.45, 0.47],
            "peach": [1.10, 0.57, 0.28],
            "scarlet": [0.35, 0.05, 0.06],
            "violet": [0.08, 0.01, 0.27]
        }
        missing = []
        for color, ctrls in self.colorOverride.items():
            if color not in colorKeys.keys():
                rgbValue = [1.00, 1.00, 1.00]

            for ctrl in ctrls:
                if not cmds.objExists(ctrl):
                    missing.append(ctrl)
                else:
                    cmds.setAttr(f"{ctrl}.overrideEnabled", 1)
                    cmds.setAttr(f"{ctrl}.overrideRGBColors", 1)
                    cmds.setAttr(f"{ctrl}.overrideColorRGB", 
                                colorKeys[color][0],
                                colorKeys[color][1],
                                colorKeys[color][2])
        if len(missing) > 0:
            print("Missing the following Controls for Color Override. . .")
            print(missing)

    def help(self):
        pass

