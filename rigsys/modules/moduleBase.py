"""Base class for all modules."""

import copy

import rigsys.utils.stringUtils as stringUtils


class ModuleBase:
    """Base class for all modules."""

    def __init__(self, rig, name: str = "", side: str = "", label: str = "", buildOrder: int = 0,
                 isMuted: bool = False, mirror: bool = False) -> None:
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
        if self.side == "M":
            print(f"Cannot mirror middle module {self.getFullName()}")
            return None

        # Don't want to copy the rig object each time
        tempRigObject = self._rig
        self._rig = None

        newModule = copy.deepcopy(self)

        self._rig = tempRigObject
        newModule._rig = tempRigObject

        # Individual variables
        for var, value in vars(self).items():
            if var in ["_rig", "dependencies", "ctrls"]:
                continue

            # Skip variables that start with an underscore
            if var.startswith("_"):
                continue

            if isinstance(value, str):
                newValue = stringUtils.mirrorString(value)
                setattr(newModule, var, newValue)

            if isinstance(value, list) or isinstance(value, tuple):
                newValue = []
                for item in value:
                    newValue.append(stringUtils.mirrorString(item))
                setattr(newModule, var, newValue)

            if isinstance(value, dict):
                newValue = {}
                for key, item in value.items():
                    newValue[stringUtils.mirrorString(key)] = stringUtils.mirrorString(item)
                setattr(newModule, var, newValue)

            else:
                setattr(newModule, var, value)

        # IMPORTANT: Anything that needs to be manually set needs to come after this point

        # So we don't get stuck in an infinite loop
        newModule.mirror = False

        if self.side == "L":
            newModule.side = "R"
        elif self.side == "R":
            newModule.side = "L"

        # TODO: Parenting

        # Proxies
        for key, proxy in self.proxies.items():
            # Don't mirror middle proxies
            if proxy.side == "M":
                continue

            newModule.proxies[key] = proxy.doMirror()

        return newModule

    def getFullName(self):
        """Return the full name of the module."""
        # TODO: @Jacob, is this the behavior we want?
        # I feel like part of the problem is that I'm still not 100% sure what self.label is for
        if self.label == "":
            return f"{self.side}_{self.name}"
        else:
            return f"{self.side}_{self.label}_{self.name}"
