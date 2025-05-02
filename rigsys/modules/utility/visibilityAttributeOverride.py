"""Build bind joints utility module."""

import logging
import    rigsys.modules.utility.utilityBase as utilityBase
import maya.cmds as cmds

logger = logging.getLogger(__name__)

class VisibilityOverride(utilityBase.UtilityModuleBase):
    """Build bind joints utility module."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 3000, isMuted: bool = False,
                 mirror: bool = False, bypassProxiesOnly: bool = False, underGroup: str = "",
                 visibilityAttrLabel: str = "", affectedObjects: list = [], attributeObject: str = "",
                 defaultValue: bool = True) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, mirror, bypassProxiesOnly)
        self.underGroup = underGroup

        self.visAttrLabel = visibilityAttrLabel
        self.affectedObjects = affectedObjects
        self.attrObject = attributeObject
        self.defaultValue = defaultValue

    def run(self) -> None:
        """Run the module."""
       # Checks
        if self.attrObject == "":
            cmds.error("AttrObject variable is empty")
        if not cmds.objExists(self.attrObject):
            cmds.error(f"{self.attrObject} does not exist.")
        if self.affectedObjects == []:
            cmds.error("affectedObjects variable is empty")
        missing = []
        for obj in self.affectedObjects:
            if not cmds.objExists(obj):
                missing.append(obj)
        if len(missing) > 0:        
            cmds.error(f"{missing} does not exist.")

        if cmds.attributeQuery("visibilityToggles", n=self.attrObject, ex=True):
            pass
        else:
            cmds.addAttr(self.attrObject, ln="visibilityToggles", 
                     at="enum", en="------", keyable=1)
            cmds.setAttr(f"{self.attrObject}.visibilityToggles", l=True)
        if self.visAttrLabel != "":
            cmds.addAttr(self.attrObject, ln=self.visAttrLabel, 
                        at="enum", en="------", keyable=1)
            cmds.setAttr(f"{self.attrObject}.visibilityToggles", l=True)
        for obj in self.affectedObjects:
            cmds.addAttr(self.attrObject, ln=obj, 
                     at="enum", en="Off:On", keyable=1)
            cmds.setAttr(f"{self.attrObject}.{obj}", self.defaultValue)
            cmds.connectAttr(f"{self.attrObject}.{obj}", f"{obj}.visibility")