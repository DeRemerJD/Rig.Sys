"""Proxy class for rigsys modules."""


class Proxy:
    """Proxy class for rigsys modules."""

    def __init__(self, position, rotation, side, label, name, parent, upVector) -> None:
        """Initialize the proxy."""
        self.position = position
        self.rotation = rotation
        self.side = side
        self.label = label
        self.name = name
        self.parent = parent
        self.upVector = upVector

    def build(self):
        """Build the proxy."""
        prx = cmds.createNode("joint", n="{}_{}_{}_proxy".format(
                            self.side, self.label, self.name
        ))

        cmds.xform(prx, ws=True, t=self.position, ro=self.rotation)

        parent = "{}_{}_{}_proxy".format(self.side, self.label, self.parent)
        cmds.parent(prx, parent)
