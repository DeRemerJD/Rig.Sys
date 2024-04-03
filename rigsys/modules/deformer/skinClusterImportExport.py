"""Build bind joints utility module."""

import logging
import rigsys.modules.deformer.deformerBase as deformerBase
import maya.cmds as cmds

logger = logging.getLogger(__name__)

class skinClusterImportExport(deformerBase.DeformerModuleBase):
    """Build bind joints utility module."""

    def __init__(self, rig, side: str = "", label: str = "", buildOrder: int = 4000, isMuted: bool = False,
                 mirror: bool = False, importSCLS: bool = False, exportSCLS: bool = False, createSCLS: bool = True,
                 joints: list = [], object: str = "", path: str = "", maxInfluences: int = 4) -> None:
        """Initialize the module."""
        super().__init__(rig, side, label, buildOrder, isMuted, mirror)

        self.obj = object
        self.joints = joints
        self.importSCLS = importSCLS
        self.exportSCLS = exportSCLS
        self.createSCLS = createSCLS
        self.path = path
        self.maxInfluences = maxInfluences

    def run(self) -> None:
        """Run the module."""
        if self.obj is not None or self.obj != "":
            if not cmds.objExists(self.obj):
                cmds.error(f"Object does not exist {self.obj}")
        if len(self.joints) != 0:
            gatherMissing = []
            for i in self.joints:
                if not cmds.objExists(i):
                    gatherMissing.append(i)
            if len(gatherMissing) > 0:
                cmds.error(f"Missing the following joints {gatherMissing}")
        if self.path is None or self.path == "":
            cmds.error(f"Path is incorrect {self.path}")
        
        if self.createSCLS:
            self.createSkinCluster()
        if self.importSCLS:
            self.readWeights()
        if self.exportSCLS:
            self.writeWeights()

    def createSkinCluster(self):
        cmds.skinCluster(self.joints, 
                         self.obj, 
                         n=f"{self.obj}_scls",
                         tsb=True,
                         mi=self.maxInfluences)

    def writeWeights(self):
        cmds.deformerWeights(f"{self.obj}_scls.xml", 
                             ex=True,
                             p=self.path,
                             deformer=f"{self.obj}_scls",
                             m="index"
                             )
    def readWeights(self):
        cmds.deformerWeights(f"{self.obj}_scls.xml", 
                             im=True,
                             p=self.path,
                             deformer=f"{self.obj}_scls",
                             m="index"
                             )