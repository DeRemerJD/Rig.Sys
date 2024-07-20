"""Base class for export modules."""

import os

import rigsys.modules.moduleBase as moduleBase


class ExportModuleBase(moduleBase.ModuleBase):
    """Base class for export modules."""

    def __init__(
        self,
        rig,
        exportPath: str,
        label: str = "",
        buildOrder: int = 5000,
        isMuted: bool = False,
        mirror: bool = False,
    ) -> None:
        """Initialize the module."""
        super().__init__(
            rig=rig, label=label, buildOrder=buildOrder, isMuted=isMuted, mirror=mirror
        )

        self.exportPath = exportPath

        self.fileName = f"{self._rig.name}_FBX"
        self.extension: str = ""

        if self.checkIfExportPathIsFile(self.exportPath):
            self.fullExportPath = self.exportPath
        else:
            self.fullExportPath = os.path.join(
                self.exportPath, self.fileName + self.extension
            )

    @staticmethod
    def checkIfExportPathIsFile(path: str) -> bool:
        """Check if the export path is a file.

        This happens by looking at the last element of the path and checking if it has a file extension.

        Arguments:
            path {str} -- Path to check

        Returns:
            bool -- Is the path a file?
        """
        if os.path.splitext(path)[1] == "":
            return False
        else:
            return True
