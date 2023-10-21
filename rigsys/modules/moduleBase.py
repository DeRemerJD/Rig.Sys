"""Base class for all modules."""
import maya.cmds as cmds

class ModuleBase:
    """Base class for all modules."""

    def __init__(self, rig, name: str = "", side: str = "", label: str = "", buildOrder: int = 0, isMuted: bool = False, mirror: bool = False) -> None:
        """Initialize the module."""
        self.name: str = name
        if self.name == "":
            self.name = type(self).__name__
        
        self.side = side
        self.label = label
        self.buildOrder: int = buildOrder
        self.dependencies: dict = {}
        self.ctrls: dict = {}
        self.isMuted: bool = isMuted
        self.isRun: bool = False
        self.mirror = mirror

        self._rig = rig

    def run(self) -> None:
        """Run the module.

        Must be implemented by all modules.
        """
        pass

    def doMirror(self):
        """Mirror the module."""
        pass

    def getFullName(self):
        """Return the full name of the module."""
        return f"{self.side}_{self.label}_{self.name}"
    
    

