"""Helper classes and function for building controls."""
import maya.cmds as cmds

class Ctrl:
    """Class to hold information on a control."""

    def __init__(self) -> None:
        """Initialize the control."""

        # Allowed shapes are
            # circle
            # square
            # box
            # sphere
        self.shape = "circle"
        self.node = ""
        pass

    def giveCtrlShape(self):
        """Give the control a shape."""
        shapes, crvNodes = self.curveLibrary(self.shape, node)
        cmds.parent(shapes, self.node, s=True, r=True)
        cmds.delete(crvNodes)

    def curveLibrary(self, shape, ctrlNode):
        '''
        This houses the allowed control shapes; by checking the allowedShapes list to
        verify if the selected type exists. Parse through the list, create a curve, 
        parse through the shapes and original curves and rename if necessary.
        '''
        shapes = []
        originalCurveNodes = []
        allowedShapes = [
        "circle", "square", "box", "sphere"
        ]
        if shape not in allowedShapes:
            shape = "circle"
        
        if shape == "circle":
            shapeObj = cmds.circle(n=ctrlNode+"_circleCurve", ch=False)[0]
            originalCurveNodes.append(shapeObj)
            childrenShapes = cmds.listRelatives(shapeObj, s=True, c=True)
            crvShape = cmds.rename(childrenShapes[0], ctrlNode+"Shape")
            shapes.append(crvShape)
            
        
        elif shape ==  "square":
            points = [
                [-1.0, 0.0, 1.0],
                [1.0, 0.0, 1.0],
                [1.0, 0.0, -1.0],
                [-1.0, 0.0, -1.0],
                [-1.0, 0.0, 1.0]
            ]
            shapeObj = cmds.curve(n=ctrlNode+"_squareCurve", p=points, d=1)
            originalCurveNodes.append(shapeObj)
            childrenShapes = cmds.listRelatives(shapeObj, s=True, c=True)
            crvShape = cmds.rename(childrenShapes[0], ctrlNode+"Shape")
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
                [-1.0, 1.0, 1.0]
                ]
            shapeObj = cmds.curve(n=ctrlNode+"_boxCurve", p=points, d=1)
            originalCurveNodes.append(shapeObj)
            childrenShapes = cmds.listRelatives(shapeObj, s=True, c=True)
            crvShape = cmds.rename(childrenShapes[0], ctrlNode+"Shape")
            shapes.append(crvShape)

        elif shape == "sphere":
            rotSets = [[0,0,0], [90,0,0], [0,0,90]]
            for i in range(3):
                shapeObj = cmds.circle(n=ctrlNode+"_sphereCurve"+str(i), ch=False)[0]
                originalCurveNodes.append(shapeObj)
                childrenShapes = cmds.listRelatives(shapeObj, s=True, c=True)
                crvShape = cmds.rename(childrenShapes[0], ctrlNode+"_{}Shape".format(i))
                shapes.append(crvShape)
                cmds.xform(shapeObj, ws=True, ro=rotSets[i])
                cmds.makeIdentity(shapeObj, a=True)

        return shapes, originalCurveNodes

            



            

