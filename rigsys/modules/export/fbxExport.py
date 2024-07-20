"""FBX Export Module."""

import os

import maya.cmds as cmds

import rigsys.modules.export.exportBase as exportBase


class FBXExport(exportBase.ExportModuleBase):
    """FBX Export Module."""

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
        """Initialize the module.

        Arguments:
            rig {rigsys.Rig} -- Rig object
            exportPath {str} -- Path to export the file to
            name {str} -- Name of the module
            buildOrder {int} -- Build order of the module
            isMuted {bool} -- Is the module muted?
            exportAll {bool} -- Export everything?
            exportSelected {bool} -- Export only selected?
            nodesToExport {list} -- List of nodes to export (if exportSelected is True)
        """
        super().__init__(rig, exportPath, label, buildOrder, isMuted, mirror)

        self.extension = ".fbx"

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
            typ="FBX export",
            preserveReferences=True,
            exportAll=self.exportAll,
            exportSelected=self.exportSelected,
        )
