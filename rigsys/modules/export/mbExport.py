"""MB Export Module."""

import os

import maya.cmds as cmds

import rigsys.modules.export.exportBase as exportBase


class MBExport(exportBase.ExportModuleBase):
    """MB Export Module."""

    def __init__(
        self,
        rig,
        exportPath: str,
        label: str = "",
        buildOrder: int = 5000,
        isMuted: bool = False,
        exportAll: bool = False,
        exportSelected: bool = False,
        nodesToExport: list = None,
        mirror: bool = False,
    ) -> None:
        """Initialize the module."""
        super().__init__(rig, exportPath, label, buildOrder, isMuted, mirror)

        self.extension = ".mb"

        self.exportAll = exportAll
        self.exportSelected = exportSelected

        if nodesToExport is None:
            nodesToExport = []

        self.nodesToExport = nodesToExport

    def run(self) -> None:
        """Run the module."""
        # Make folders, if necessary
        exportDir = os.path.dirname(self.fullExportPath)
        if not os.path.exists(exportDir):
            os.makedirs(exportDir)

        if self.exportSelected:
            cmds.select(self.nodesToExport, r=True)

        cmds.file(
            self.fullExportPath,
            force=True,
            options="v=0;",
            typ="mayaBinary",
            preserveReferences=True,
            exportAll=self.exportAll,
            exportSelected=self.exportSelected,
        )
