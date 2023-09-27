"""Base class for export modules."""


import rigsys.modules.moduleBase as moduleBase


class ExportModuleBase(moduleBase.ModuleBase):
    """Base class for export modules."""

    def __init__(self) -> None:
        """Initialize the module."""
        super().__init__()
        self.buildOrder = 5000

        self.exportPath: str = ""
        self.fileName: str = ""
        self.extension: str = ""
