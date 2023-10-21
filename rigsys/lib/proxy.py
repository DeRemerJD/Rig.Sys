"""Proxy class for rigsys modules."""
import maya.cmds as cmds

class Proxy:
    """Proxy class for rigsys modules."""

    def __init__(self, position=[0.0, 0.0, 0.0], rotation=[0.0, 0.0, 0.0], 
                side="M", label="", name="", parent=None, upVector=False,
                plug=False) -> None:
        """Initialize the proxy."""
        self.position = position
        self.rotation = rotation
        self.side = side
        self.label = label
        self.name = name
        self.parent = parent
        self.upVector = upVector
        self.plug = plug

    def build(self):
        """Build the proxy."""
        prx = cmds.createNode("joint", n="{}_{}_{}_proxy".format(
                            self.side, self.label, self.name
        ))

        cmds.xform(prx, ws=True, t=self.position, ro=self.rotation)
        if self.parent:
            parent = "{}_{}_{}_proxy".format(self.side, self.label, self.parent)
            cmds.parent(prx, parent)
