"""Python Utility module."""

import logging
import os

from rigsys.modules.utility.utilityBase import UtilityModuleBase


logger = logging.getLogger(__name__)


class PythonCode(UtilityModuleBase):
    """Python utility module.

    Takes in a path to a python file and executes it."""

    def __init__(self, rig, pythonFile: str, label: str = "", buildOrder: int = 3000, isMuted: bool = False) -> None:
        side = "M"
        mirror = False
        super().__init__(rig, side, label, buildOrder, isMuted, mirror)

        self.pythonFile = pythonFile

    def run(self):
        """Run the module (execute the python file)."""
        if not os.path.exists(self.pythonFile):
            raise ValueError(f"File does not exist: {self.pythonFile}")

        with open(self.pythonFile) as f:
            code = compile(f.read(), self.pythonFile, 'exec')
            exec(code, globals(), locals())
