"""Functions for working with nurbs."""

import maya.cmds as cmds

import rigsys.utils.listUtils as listUtils


def returnNurbsCVs(target, orderRows=False, direction="u"):
    """Find all the components of a nurbs, curve, or poly object."""
    # Get all the shapes of the target object
    shapes = cmds.listRelatives(target, shapes=True)

    # If the target is a list, use the first element as the target
    if isinstance(target, list):
        target = target[0]

    # Initialize an empty list to store the components
    results = []

    # Store the current selection so we can restore it later
    orig = cmds.ls(sl=True)

    # Loop over each shape and retrieve its components
    for shape in shapes:
        # Check if the shape is not an intermediate shape
        sEnd = shape[-4:]
        if sEnd != "Orig":
            # Get the type of the shape
            sType = cmds.objectType(shape)

            # If the shape is a mesh, retrieve its vertices
            if sType == "mesh":
                components = []
                vCount = cmds.polyEvaluate((shape), v=1)
                for x in range(0, vCount):
                    comp = "{}.vtx[{}]".format(shape, x)
                    components.append(comp)
                results.append(components)

            # If the shape is a nurbs curve, retrieve its control vertices (CVs)
            elif sType == "nurbsCurve":
                components = []
                cvs = cmds.getAttr("{}.cv[*]".format(shape))
                cvNum = len(cvs)
                for x in range(0, cvNum):
                    comp = "{}.cv[{}]".format(shape, x)
                    components.append(comp)
                results.append(components)

            # If the shape is a nurbs surface, retrieve its CVs
            elif sType == "nurbsSurface":
                # Select all the CVs of the surface
                cmds.select("{}.cv[*][*]".format(shape))
                cvs = cmds.ls(sl=True, flatten=True)

                # Determine the maximum U and V values of the CVs
                sU = 0
                sV = 0
                for cv in cvs:
                    toks = cv.split("[")
                    uval = toks[1].split("]")
                    uval = int(uval[0])
                    vval = toks[2].split("]")
                    vval = int(vval[0])
                    if uval > sU:
                        sU = uval
                    if vval > sV:
                        sV = vval
                sU += 1
                sV += 1

                # Build the list of CVs
                for x in range(0, sU):
                    for y in range(0, sV):
                        comp = "{}.cv[{}][{}]".format(shape, x, y)
                        results.append(comp)

                # Restore the original selection
                cmds.select(orig)

    # Flatten the list of components
    results = listUtils.flattenList(results)

    # If orderRows is True, order the components into rows based on the direction argument
    if orderRows:
        rowU = 0
        rowV = 0
        for component in results:
            toks = component.split("[")
            uVal = toks[1].split("]")
            uVal = int(uVal[0])
            vVal = toks[2].split("]")
            vVal = int(vVal[0])
            if uVal > rowU:
                rowU = uVal
            if vVal > rowV:
                rowV = vVal
        rowU += 1
        rowV += 1
        rows = []
        if direction.lower() == "u":
            for u in range(0, rowU):
                row = []
                for v in range(0, rowV):
                    component = "{}.cv[{}][{}]".format(target, u, v)
                    row.append(component)
                rows.append(row)
        elif direction.lower() == "v":
            for x in range(0, rowV):
                row = []
                for y in range(0, rowU):
                    component = "{}.cv[{}][{}]".format(target, y, x)
                    row.append(component)
                rows.append(row)
        results = rows

    # Return the list of components
    return results
