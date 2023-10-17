"""Proxy class for rigsys modules."""

# TODO: @Jacob - at Zubio we had proxies for nurbs, curves, etc. Do we want any of those here?

import copy


class Proxy:
    """Proxy class for rigsys modules."""

    def __init__(self, side: str, label: str, position: list = None, rotation: list = None) -> None:
        """Initialize the proxy."""
        self.side = side
        self.label = label
        if position is None:
            position = [0, 0, 0]
        if rotation is None:
            rotation = [0, 0, 0]
        self.position = position
        self.rotation = rotation

    def build(self):
        """Build the proxy."""
        pass

    def getFullName(self):
        """Return the full name of the proxy."""
        return f"{self.side}_{self.label}"

    def doMirror(self):
        """Mirror the proxy, returning a new proxy object."""
        if self.side == "M":
            print(f"Cannot mirror middle proxy {self.getFullName()}")
            return None

        newProxy = copy.deepcopy(self)

        if self.side == "L":
            newProxy.side = "R"
        elif self.side == "R":
            newProxy.side = "L"

        # Transform data
        # TODO: @Jacob, I copied this from the zubio proxies, make sure this is correct
        newProxy.position[0] *= -1
        newProxy.rotation[0] *= -1
        newProxy.rotation[1] *= -1
        newProxy.rotation[2] *= -1

        return newProxy
