"""Helper classes and function for building controls."""
import maya.cmds as cmds


class Ctrl:
    """Class to hold information on a control."""

    def __init__(self, node: str = "", shape: str = "circle", scale: list = None,
                 orient: list = None, offset: list = None) -> None:
        """Initialize the control."""
        # Allowed shapes are
        # circle
        # square
        # box
        # sphere

        if scale is None:
            scale = [1.0, 1.0, 1.0]
        if orient is None:
            orient = [0.0, 0.0, 0.0]
        if offset is None:
            offset = [0.0, 0.0, 0.0]

        self.shape = shape
        self.node = node
        self.scale = scale
        self.orient = orient
        self.offset = offset

    def giveCtrlShape(self):
        """Give the control a shape."""
        shapes, crvNodes = self.curveLibrary(self.shape)
        cmds.parent(shapes, self.node, s=True, r=True)
        cmds.delete(crvNodes)

    def curveLibrary(self, shape):
        """Curve library for the control shapes.

        This houses the allowed control shapes; by checking the allowedShapes list to
        verify if the selected type exists. Parse through the list, create a curve,
        parse through the shapes and original curves and rename if necessary.
        """
        shapes = []
        originalCurveNodes = []
        allowedShapes = ["circle", "square", "box", "sphere"]
        if shape not in allowedShapes:
            shape = "circle"

        if shape == "circle":
            shapeObj = cmds.circle(n=self.node + "_circleCurve", ch=False)[0]
            originalCurveNodes.append(shapeObj)
            childrenShapes = cmds.listRelatives(shapeObj, s=True, c=True)
            crvShape = cmds.rename(childrenShapes[0], self.node + "Shape")
            shapes.append(crvShape)

        elif shape == "square":
            points = [
                [-1.0, 0.0, 1.0],
                [1.0, 0.0, 1.0],
                [1.0, 0.0, -1.0],
                [-1.0, 0.0, -1.0],
                [-1.0, 0.0, 1.0],
            ]
            shapeObj = cmds.curve(n=self.node + "_squareCurve", p=points, d=1)
            originalCurveNodes.append(shapeObj)
            childrenShapes = cmds.listRelatives(shapeObj, s=True, c=True)
            crvShape = cmds.rename(childrenShapes[0], self.node + "Shape")
            shapes.append(crvShape)

        elif shape == "box":
            points = [
                [-1.0, -1.0, 1.0],
                [1.0, -1.0, 1.0],
                [1.0, 1.0, 1.0],
                [1.0, 1.0, -1.0],
                [1.0, -1.0, -1.0],
                [-1.0, -1.0, -1.0],
                [-1.0, 1.0, -1.0],
                [-1.0, 1.0, 1.0],
                [-1.0, -1.0, 1.0],
                [-1.0, -1.0, -1.0],
                [-1.0, 1.0, -1.0],
                [1.0, 1.0, -1.0],
                [1.0, -1.0, -1.0],
                [1.0, -1.0, 1.0],
                [1.0, 1.0, 1.0],
                [-1.0, 1.0, 1.0],
            ]
            shapeObj = cmds.curve(n=self.node + "_boxCurve", p=points, d=1)
            originalCurveNodes.append(shapeObj)
            childrenShapes = cmds.listRelatives(shapeObj, s=True, c=True)
            crvShape = cmds.rename(childrenShapes[0], self.node + "Shape")
            shapes.append(crvShape)

        elif shape == "sphere":
            rotSets = [[0, 0, 0], [90, 0, 0], [0, 90, 0]]
            for i in range(3):
                shapeObj = cmds.circle(n=self.node + "_sphereCurve" + str(i), ch=False)[
                    0
                ]
                originalCurveNodes.append(shapeObj)
                childrenShapes = cmds.listRelatives(shapeObj, s=True, c=True)
                crvShape = cmds.rename(
                    childrenShapes[0], self.node + "_{}Shape".format(i)
                )
                shapes.append(crvShape)
                cmds.xform(shapeObj, ws=True, ro=rotSets[i])
                cmds.makeIdentity(shapeObj, a=True)

        for crvNode in originalCurveNodes:
            cmds.xform(crvNode, a=True, s=self.scale)
            cmds.xform(crvNode, r=True, ro=self.orient)
            cmds.xform(crvNode, r=True, t=self.offset)
            cmds.makeIdentity(crvNode, a=True)

        return shapes, originalCurveNodes
