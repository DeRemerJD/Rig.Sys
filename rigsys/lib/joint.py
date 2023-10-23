"""Helper classes and functions for building joints."""
import maya.cmds as cmds


def createJoint(jointName, position=None, rotation=None, mirrorPosition=False,
                mirrorRotation=False, freeze=False,):
    """Create a joint with the given name, position, and rotation."""
    if position is None:
        position = [0.0, 0.0, 0.0]
    if rotation is None:
        rotation = [0.0, 0.0, 0.0]

    joint = cmds.createNode("joint", n=jointName)
    cmds.xform(joint, ws=True, t=position)
    cmds.xform(joint, ws=True, ro=rotation)
    mirrorJoints(joint, mirrorPosition, mirrorRotation)
    if freeze:
        cmds.makeIdentity(joint, a=True)
    return joint


def aim(nodes=[], target=[], aimAxis="+x", upAxis="-z", upObj=None, vector="-z", upType="object", objRot=None,
        match=False, rotateOrder="xyz",):
    """Aim a series of nodes at a target."""
    # Check the nodes
    dontExist = []
    if nodes == []:
        return
    else:
        if nodes:
            for i in nodes:
                if not cmds.objExists(i):
                    dontExist.append(i)
            if len(dontExist) > 0:
                cmds.error("The Following Nodes " + str(dontExist))

    if len(nodes) < 2:
        cmds.error("Length Of Nodes Must Be At Least Two")

    if target == []:
        return
    else:
        if target:
            for i in target:
                if not cmds.objExists(i):
                    dontExist.append(i)
            if len(dontExist) > 0:
                cmds.error("The Following Nodes " + str(dontExist))

    # Get the aiming information.
    # Sanity Checks
    if upObj is None:
        upType = "vector"
    elif upObj == "objectrotation":
        if not objRot:
            objRot = upObj
            if not cmds.objExists(upObj):
                cmds.error("UpObject Does Not Exist: " + upObj)
        else:
            if not cmds.objExists(objRot):
                cmds.error("UpObject Does Not Exist: " + objRot)

    elif upType == "object":
        if not cmds.objExists(upObj):
            cmds.error("UpObject Does Not Exist: " + upObj)

    aimVector = axisToVector(aimAxis)
    upVector = axisToVector(upAxis)
    worldVector = axisToVector(vector)
    rotateOrderVal = rotateOrderToEnumValue(rotateOrder)

    # Cycle through each node.
    for x in nodes:
        cmds.setAttr(x + ".rotateOrder", rotateOrderVal)
        # Aim!
        if upObj == "vector":
            ac = cmds.aimConstraint(
                target, nodes[x], aim=aimVector, wut=upType, u=upVector, wu=worldVector
            )
        else:
            ac = cmds.aimConstraint(
                target, nodes[x], aim=aimVector, wut=upType, wuo=upObj, u=upVector
            )
        cmds.delete(ac)

    if match:
        if len(nodes) >= 2:
            matchAx = getMatchAxis(aimAxis[0])
            matchVal = cmds.getAttr("{0}.r{1}".format(nodes[0], matchAx))
            for node in nodes[1:]:
                cmds.setAttr("{0}.r{1}".format(node, matchAx), matchVal)


# Aim a series of nodes down a chain.
def aimSequence(targets=[], aimAxis="+x", upAxis="-z", upObj=None, vector="-z", upType="object", objRot=None,
                rotateOrder="xyz",):
    dontExist = []
    if targets == []:
        return
    else:
        if targets:
            for i in targets:
                if not cmds.objExists(i):
                    dontExist.append(i)
            if len(dontExist) > 0:
                cmds.error("The Following Nodes " + str(dontExist))

    if len(targets) < 2:
        cmds.error("Length Of Nodes Must Be At Least Two")

    # Get Vector And Enum Values
    aimVector = axisToVector(aimAxis)
    upVector = axisToVector(upAxis)
    worldVector = axisToVector(vector)
    rotateOrderVal = rotateOrderToEnumValue(rotateOrder)

    # Cycle through each target.
    for i in range(0, len(targets)):
        # Check for Children and unparent/reparent
        childs = cmds.listRelatives(targets[i], c=1, type="transform")
        if childs:
            cmds.parent(childs, w=1)

        cmds.setAttr(i + ".rotateOrder", rotateOrderVal)

        # If this is the last item in the loop, match orientations to previous item.
        if targets[i] == targets[-1]:
            for axis in ("x", "y", "z"):
                previousRotation = cmds.xform(targets[i - 1], q=True, a=True, ro=True)
                cmds.xform(targets[i], a=True, ro=previousRotation)

                if cmds.objectType(targets[i]) == "joint":
                    cJnts = cmds.listRelatives(targets[i - 1], children=True)
                    if cJnts is not None:
                        if targets[i] in cJnts:
                            cmds.setAttr(targets[i] + ".jointOrient" + axis, 0)
                            cmds.setAttr(targets[i] + ".rotate" + axis, 0)

        # Otherwise, aim it properly.
        else:
            if upObj == "vector":
                ac = cmds.aimConstraint(
                    targets[i + 1],
                    targets[i],
                    aim=aimVector,
                    wut=upType,
                    u=upVector,
                    wu=worldVector,
                )
            else:
                ac = cmds.aimConstraint(
                    targets[i + 1],
                    targets[i],
                    aim=aimVector,
                    wut=upType,
                    wuo=upObj,
                    u=upVector,
                    wu=worldVector,
                )
            cmds.delete(ac)

        if childs:
            cmds.parent(childs, targets[i])


def mirrorJoints(joints, position=True, rotation=True, freeze=False):
    """Mirror the given joints on the YZ plane."""""
    # TODO: Add other mirroring types
    if type(joints) is not list:
        joints = [joints]

    for joint in joints:
        t = cmds.xform(joint, q=True, ws=True, t=True)
        ro = cmds.xform(joint, q=True, ws=True, ws=True)
        if position:
            t[0] = t[0] * -1
        if rotation:
            ro[0] = ro[0] + 180
            ro[1] = ro[1] * -1
            ro[2] = ro[2] * -1
        if freeze:
            cmds.makeIdentity


# Function that takes a string vector and returns the proper numerical vector.
def axisToVector(axis):
    vec = None
    if axis == "+x":
        vec = [1, 0, 0]
    elif axis == "-x":
        vec = [-1, 0, 0]
    elif axis == "+y":
        vec = [0, 1, 0]
    elif axis == "-y":
        vec = [0, -1, 0]
    elif axis == "+z":
        vec = [0, 0, 1]
    elif axis == "-z":
        vec = [0, 0, -1]
    return vec


# Function that finds the axis that needs to be matched.
def getMatchAxis(axis):

    matchAxis = None
    if isinstance(axis, list):
        if axis == [1, 0, 0] or axis == [-1, 0, 0]:
            matchAxis = "x"
        elif axis == [0, 1, 0] or axis == [0, -1, 0]:
            matchAxis = "y"
        elif axis == [0, 0, 1] or axis == [0, 0, -1]:
            matchAxis = "z"
    elif isinstance(axis, str):
        if "x" in axis:
            matchAxis = "x"
        elif "y" in axis:
            matchAxis = "y"
        elif "z" in axis:
            matchAxis = "z"
    return matchAxis


def rotateOrderToEnumValue(rotateOrder):
    rotateOrder = rotateOrder.lower()
    enumVal = None
    if rotateOrder == "xyz":
        enumVal = 0
    elif rotateOrder == "yzx":
        enumVal = 1
    elif rotateOrder == "zxy":
        enumVal = 2
    elif rotateOrder == "xzy":
        enumVal = 3
    elif rotateOrder == "yxz":
        enumVal = 4
    elif rotateOrder == "zyx":
        enumVal = 5
    return enumVal
