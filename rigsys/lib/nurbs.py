"""Functions for working with nurbs."""

import maya.cmds as cmds

import rigsys.utils.listUtils as listUtils


def returnNurbsCVs(target, orderRows=False, direction="u"):
    """Find all the components of a nurbs,curve,or poly object."""
    shapes = cmds.listRelatives(target, shapes=True)

    if isinstance(target, list):
        target = target[0]

    results = []
    orig = cmds.ls(sl=True)
    for shape in shapes:
        sEnd = shape[-4:]

        if sEnd != "Orig":
            sType = cmds.objectType(shape)

            if sType == "mesh":
                components = []
                vCount = cmds.polyEvaluate((shape), v=1)

                for x in range(0, vCount):
                    comp = "{}.vtx[{}]".format(shape, x)
                    components.append(comp)

                results.append(components)

            elif sType == "nurbsCurve":
                components = []
                cvs = cmds.getAttr("{}.cv[*]".format(shape))
                cvNum = len(cvs)

                for x in range(0, cvNum):
                    comp = "{}.cv[{}]".format(shape, x)
                    components.append(comp)

                results.append(components)

            elif sType == "nurbsSurface":
                cmds.select("{}.cv[*][*]".format(shape))
                cvs = cmds.ls(sl=True, flatten=True)
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

                for x in range(0, sU):
                    for y in range(0, sV):
                        comp = "{}.cv[{}][{}]".format(shape, x, y)
                        results.append(comp)

                cmds.select(orig)

    results = listUtils.flattenList(results)

    if orderRows:
        rowU = 0
        rowV = 0

        for component in results:
            toks = component.split("[")
            uVal = toks[1].split("]")
            uVal = int(uVal[0])
            vVal = toks[2].split("]")
            vVal = int(vVal[0])
            # This determines rows, if the value is greater than the current row, it adds a row.
            if uVal > rowU:
                rowU = uVal

            if vVal > rowV:
                rowV = vVal

        # This basically adds a root level/top level control ring.
        rowU += 1
        rowV += 1
        rows = []

        # Gets the direction set by the user and build along the U or V param/direction.
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
    return results
