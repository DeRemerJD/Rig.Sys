"""Pure Python implementation of the transferSkinCluster plugin.

This module contains the following functions:
    - writeWeights: Write the weights to the specified file to the selected object.
    - readWeights: Read the weights from the specified file to the selected object.

    - writeWeightsOld: Write the weights to the specified file to the selected object.
    - readWeightsOld: Read the weights from the specified file to the selected object.

The "old" functions are the original OpenMaya functions that were used in the transferSkinCluster plugin. They are
generally much faster, but they are not as robust as the new functions. The new functions are pure Python and do not
require the OpenMaya API. They are also more robust and can handle more situations. However, they are much slower than
the old functions.

The readWeights function can detect between new and old versions of scw files and will properly read them. The
writeWeights function will always write the new version of the scw file.

Example usage:

import maya.cmds as cmds

obj = cmds.polySphere()[0]
cmds.select(obj)

skinClusterTransfer.writeWeights("path/to/weights/obj.scw")
skinClusterTransfer.readWeights("path/to/weights/obj.scw")
"""

import logging

import maya.OpenMaya as OpenMaya
import maya.OpenMayaAnim as OpenMayaAnim
import maya.cmds as cmds
import maya.mel as mel

import rigsys.lib.nurbs as nurbs

logger = logging.getLogger(__name__)


def writeSCLS(objects: list = [], path: str = "", suffix: str = "scls"):
    if len(objects) == 0:
        objects = cmds.ls(sl=1)
        if len(objects) == 0:
            cmds.error("No Objects provided or selected.")
    if path == "":
        cmds.error("Path is empty")

    for obj in objects:
        cmds.deformerWeights(f"{obj}_{suffix}.json",
                             ex=True,
                             p=path,
                             deformer=f"{obj}_{suffix}",
                             at=["maintainMaxInfluences", "maxInfluences"],
                             method="index",
                             format="JSON",
                             dv=1.0
                             )


def readSCLS(objects: list = [], path: str = "", suffix: str = "scls"):
    if len(objects) == 0:
        objects = cmds.ls(sl=1)
        if len(objects) == 0:
            cmds.error("No Objects provided or selected.")
    if path == "":
        cmds.error("Path is empty")

    for obj in objects:
        cmds.deformerWeights(f"{obj}_{suffix}.json",
                             im=True,
                             p=path,
                             deformer=f"{obj}_{suffix}",
                             at=["maintainMaxInfluences", "maxInfluences"],
                             method="index",
                             format="JSON",
                             dv=1.0
                             )


def createSCLS(object: str = "", joints: list = [], suffix: str = "scls", maxInfluences=4):
    if object == "":
        object = cmds.ls(sl=1)[-1]
        if len(object) == 0:
            if not cmds.objExists(object):
                cmds.error("No Object provided or selected.")
    if len(joints) == 0:
        joints = cmds.ls(sl=1)[0:-1]
        if len(joints) == 0:
            cmds.error("Mo Joints Provided")

    cmds.skinCluster(joints,
                     object,
                     n=f"{object}_{suffix}",
                     tsb=True,
                     mi=maxInfluences)


def getSelectedJoints():
    print(cmds.ls(sl=1))


# def writeWeights(fileName):
#     """Write the weights to the specified file."""
#     try:
#         weightFile = open(fileName, 'w')
#     except Exception:
#         cmds.error(f"Error opening file: {fileName}")

#     sel = cmds.ls(sl=True)

#     for obj in sel:
#         shape = obj
#         if cmds.objectType(obj) == 'transform':
#             shape = cmds.listRelatives(obj, c=True, s=True)[0]
#         objType = cmds.objectType(shape)

#         if objType == "skinCluster":
#             # Get the affected node of the skin cluster node
#             shape = cmds.skinCluster(obj, q=True, g=True)[0]
#             obj = cmds.listRelatives(shape, p=True)[0]
#             objType = cmds.objectType(shape)

#         allInfluences = set()
#         allWeightData = ""

#         if objType == "mesh":
#             numVerts = cmds.polyEvaluate(obj, v=True)
#             numVerts = range(numVerts)
#         elif objType == "nurbsSurface":
#             numVerts = nurbs.returnNurbsCVs(obj)
#         else:
#             # Unsupported object type
#             weightFile.close()
#             cmds.error("Object type not supported")
#             return

#         for i in numVerts:
#             if objType == "mesh":
#                 influences = cmds.skinCluster(f"{obj}.vtx[{i}]", q=True, inf=True)
#             elif objType == "nurbsSurface":
#                 influences = cmds.skinPercent(f"{obj}_scls", i, q=True, t=None)

#             for influence in influences:
#                 allInfluences.add(influence)

#             if objType == "mesh":
#                 weights = cmds.skinPercent(f"{obj}_scls", f"{obj}.vtx[{i}]", q=True, value=True)
#             elif objType == "nurbsSurface":
#                 weights = cmds.skinPercent(f"{obj}_scls", i, q=True, value=True)
#                 if len(weights) != len(influences):
#                     cmds.warning(f"Number of weights ({len(weights)}) does not match number of influences "
#                                  f"({len(influences)}) for {obj} {i}")

#             for j, influence in enumerate(influences):
#                 if float(weights[j]) == 0.0:
#                     continue

#                 if objType == "mesh":
#                     index = i
#                 elif objType == "nurbsSurface":
#                     index1 = i.split('[')[1].split(']')[0]
#                     index2 = i.split('[')[2].split(']')[0]
#                     index = f"{index1},{index2}"

#                 allWeightData += f"{index} {influence} {weights[j]}\n"

#         # Write the data to the file
#         weightFile.write(f"skinClusterData {objType}\n")  # To differentiate from old files
#         for influence in allInfluences:
#             weightFile.write(f"{influence} ")
#         _writeSclsInfo(weightFile, obj, shape)

#         weightFile.write(allWeightData)

#     weightFile.close()


# def readWeights(fileName, reverseOrder=False, specifics=None):
#     """Read the weights from a file and sets them on the skinCluster node."""
#     # Open the file for reading
#     try:
#         weightFile = open(fileName, 'r')
#     except Exception:
#         cmds.warning(f"Error opening skin weights file: {fileName}")
#         return -1

#     # Get the first line of the file
#     lines = weightFile.readlines()
#     line = lines[0]

#     # Check if the file is an old file
#     if not line.startswith("skinClusterData"):
#         readWeightsOld(fileName, reverseOrder, specifics)
#         return

#     objType = line.split(" ")[1].strip()
#     influences = [infl for infl in lines[1].split(" ") if infl != "" and infl != "\n"]
#     shape = lines[2].strip()
#     skinClusterName = lines[3].strip()
#     skinClusterVars = lines[4]
#     if skinClusterVars.endswith("\n"):
#         skinClusterVars = skinClusterVars[:-1]
#     weightData = lines[5:]

#     normalization = 1

#     # Close the file
#     weightFile.close()

#     # Check for missing items
#     missingItems = []
#     for infl in influences:
#         if not cmds.objExists(infl):
#             missingItems.append(infl)

#     if not cmds.objExists(shape):
#         missingItems.append(shape)

#     if len(missingItems) > 0:
#         logger.warning(f"{skinClusterName} is missing the following skinCluster affectors:\n")
#         for item in missingItems:
#             logger.warning(f"\t{item}")
#         return -1

#     try:
#         cmds.select(influences + [shape], r=True)
#     except Exception as e:
#         cmds.error(f"Error selecting {shape}: {e}")
#         return -1

#     if not specifics:
#         # Check if the geo is not already bound
#         history = cmds.listHistory(shape, f=0, bf=1)
#         isHistoryFound = False
#         for h in history:
#             if cmds.nodeType(h) == "skinCluster":
#                 logger.warning(f"{shape} is already bound to a skinCluster.")
#                 isHistoryFound = True
#         if isHistoryFound:
#             return -1

#         # Create the skinCluster
#         melCommand = f'newSkinCluster \"-tsb -bm 0 {skinClusterVars} -omi true -rui false\"'
#         newSkinCluster = mel.eval(melCommand)[0]
#         cmds.rename(newSkinCluster, skinClusterName)

#         normalization = cmds.getAttr(f"{skinClusterName}.nw")
#         cmds.setAttr(f"{skinClusterName}.nw", 0)
#         cmds.skinPercent(skinClusterName, shape, prw=100, nrm=0)

#     obj = cmds.listRelatives(shape, p=True)[0]
#     constructorValues = []
#     constructorList = []
#     for lineNumber, line in enumerate(weightData):
#         if line == "":
#             continue

#         line = line.split(" ")
#         if objType == "mesh":
#             index = int(line[0])
#         elif objType == "nurbsSurface":
#             index = line[0].split(",")
#         influence = line[1]
#         weight = float(line[2])

#         if weight == 0.0:
#             continue

#         # if reverseOrder:
#         #     influence = influences[-1 - influences.index(influence)]

#         if objType == "mesh":
#             newVert = False

#             if skinClusterName not in constructorList:
#                 constructorList.append(skinClusterName)

#             if obj not in constructorList:
#                 constructorList.append(obj)

#             if index not in constructorList:
#                 constructorList.append(index)

#             # Look one line ahead to see if the next line is a new vertex
#             nextLineIndex = lineNumber + 1
#             if nextLineIndex < len(weightData):

#                 nextIndex = weightData[nextLineIndex].split(" ")[0]

#                 if int(index) != int(nextIndex):
#                     newVert = True
#                 else:
#                     newVert = False
#             else:
#                 newVert = True

#             if index == constructorList[2]:
#                 constructorList.append([influence, weight])

#             if newVert is True:

#                 constructorValues.append(constructorList)
#                 constructorList = []

#         elif objType == "nurbsSurface":
#             cmds.skinPercent(skinClusterName, obj + f".cv[{index[0]}][{index[1]}]", tv=[influence, weight])

#     if objType == "mesh":
#         for constructor in constructorValues:
#             cmds.skinPercent(constructor[0], f"{constructor[1]}.vtx[{constructor[2]}]", tv=constructor[3:])

#     cmds.setAttr(f"{skinClusterName}.nw", normalization)


# def writeWeightsOld(fileName):
#     """Write the weights to the specified file."""
#     # get the current selection
#     skinClusterNode = cmds.ls(sl=True, fl=True)
#     if len(skinClusterNode) != 0:
#         skinClusterNode = skinClusterNode[0]
#     else:
#         OpenMaya.MGlobal.displayError('Select a skinCluster node to export.')
#         return -1

#     # check if it's a skinCluster
#     if cmds.nodeType(skinClusterNode) != 'skinCluster':
#         OpenMaya.MGlobal.displayError('Selected node is not a skinCluster.')
#         return -1

#     # get the MFnSkinCluster
#     sel = OpenMaya.MSelectionList()
#     OpenMaya.MGlobal.getActiveSelectionList(sel)
#     skinClusterObject = OpenMaya.MObject()
#     sel.getDependNode(0, skinClusterObject)
#     skinClusterFn = OpenMayaAnim.MFnSkinCluster(skinClusterObject)

#     # get the influence objects
#     infls = cmds.skinCluster(skinClusterNode, q=True, inf=True)
#     if len(infls) == 0:
#         OpenMaya.MGlobal.displayError('No influence objects found for skinCluster %s.' % skinClusterNode)
#         return -1

#     # get the connected shape node
#     shape = cmds.skinCluster(skinClusterNode, q=True, g=True)[0]
#     if len(infls) == 0:
#         OpenMaya.MGlobal.displayError('No connected shape nodes found.')
#         return (-1)

#     # get the dag path of the shape node
#     cmds.select(shape, r=True)
#     sel = OpenMaya.MSelectionList()
#     OpenMaya.MGlobal.getActiveSelectionList(sel)
#     shapeDag = OpenMaya.MDagPath()
#     sel.getDagPath(0, shapeDag)
#     # create the geometry iterator
#     geoIter = OpenMaya.MItGeometry(shapeDag)

#     # open the file for writing
#     try:
#         weightFile = open(fileName, 'wb')
#     except Exception:
#         OpenMaya.MGlobal.displayError('A file error has occurred for file \'' + fileName + '\'.')
#         return -1

#     # write all influences and the shape node to the file
#     for infl in infls:
#         if not isinstance(infl, bytes):
#             infl = str.encode(str(infl) + ' ')
#         weightFile.write(infl)

#     if not isinstance(shape, bytes):
#         shape = str.encode(str(shape) + '\n')
#     weightFile.write(shape)

#     if not isinstance(skinClusterNode, bytes):
#         tempSkinClusterNode = str.encode(str(skinClusterNode) + '\n')
#     else:
#         tempSkinClusterNode = skinClusterNode + '\n'
#     weightFile.write(tempSkinClusterNode)

#     # write the attributes of the skinCluster node to the file
#     result = cmds.getAttr(skinClusterNode + ".normalizeWeights")
#     if not isinstance(result, bytes):
#         result = str.encode("-nw {} ".format(result))
#     weightFile.write(result)
#     result = cmds.getAttr(skinClusterNode + ".maxInfluences")
#     if not isinstance(result, bytes):
#         result = str.encode("-mi {} ".format(result))
#     weightFile.write(result)
#     result = cmds.getAttr(skinClusterNode + ".dropoff")[0][0]
#     if not isinstance(result, bytes):
#         result = str.encode("-dr {} ".format(result))
#     weightFile.write(result)
#     weightFile.write(str.encode('\n'))

#     # create a pointer object for the influence count of the MFnSkinCluster
#     infCount = OpenMaya.MScriptUtil()
#     infCountPtr = infCount.asUintPtr()
#     OpenMaya.MScriptUtil.setUint(infCountPtr, 0)

#     # get the skinCluster weights
#     value = OpenMaya.MDoubleArray()
#     while not geoIter.isDone():
#         skinClusterFn.getWeights(shapeDag, geoIter.currentItem(), value, infCountPtr)
#         for j in range(0, len(infls)):
#             if value[j] > 0:
#                 lineArray = [geoIter.index(), infls[j], j, value[j]]
#                 lineArray = str.encode(str(lineArray) + '\n')
#                 weightFile.write(lineArray)
#         geoIter.next()

#     weightFile.close()
#     return (1)


# def readWeightsOld(fileName, reverseOrder=False, specifics=None):
#     """Read the weights from a file and sets them on the skinCluster node."""
#     # open the file for reading
#     try:
#         weightFile = open(fileName, 'rb')
#     except Exception:
#         OpenMaya.MGlobal.displayError('A file error has occurred for file \'' + fileName + '\'.')
#         return -1

#     weightData = weightFile.read()
#     if isinstance(weightData, bytes):
#         weightData = weightData.decode()
#     weightData = weightData.replace('\r', '')
#     weightLines = weightData.split('\n')
#     weightFile.close()

#     normalization = 1

#     # variables for writing a range of influences
#     # Imagine actually putting the variables near where they're used??
#     weightString = ''
#     inflStart = -1
#     inflEnd = -1
#     setCount = 0
#     writeData = 0

#     # --------------------------------------------------------------------------------
#     # the first line contains the joints and skin shape
#     # --------------------------------------------------------------------------------
#     objects = weightLines[0]
#     items = objects.split(' ')
#     shape = items[len(items) - 1]

#     # --------------------------------------------------------------------------------
#     # the second line contains the name of the skin cluster
#     # --------------------------------------------------------------------------------
#     skinClusterName = weightLines[1]

#     # --------------------------------------------------------------------------------
#     # the third line contains the values for the skin cluster
#     # --------------------------------------------------------------------------------
#     # Imagine writing documentation that is actually correct??
#     objects = objects.split(' ')
#     if reverseOrder == 1:
#         objects = objects[::-1]
#         objects.pop(0)
#         objects.append(shape)

#     # Check for missing affectors
#     missingItems = []
#     for item in objects:
#         if not cmds.objExists(item):
#             missingItems.append(item)

#     if missingItems:
#         OpenMaya.MGlobal.displayError('[' + skinClusterName + '] is missing the following skinCluster affectors:\n')

#     for item in missingItems:
#         logger.warning(item)

#     if missingItems:
#         return -1
#     # select the influences and the skin shape
#     try:
#         cmds.select(objects, r=True)
#     except Exception:
#         # weightFile.close()  # The file should already be closed by this point
#         return -1

#     if not specifics:
#         # check if the geometry is not already bound
#         history = cmds.listHistory(shape, f=0, bf=1)
#         for h in history:
#             if cmds.nodeType(h) == 'skinCluster':
#                 OpenMaya.MGlobal.displayError(shape + ' is already connected to a skinCluster.')
#                 return -1

#         # check for the version
#         # up to Maya 2012 the bind method flag is not available
#         version = mel.eval('getApplicationVersionAsFloat()')
#         bindMethod = '-bm 0 '
#         if version < 2013:
#             bindMethod = '-ih '

#         # create the new skinCluster
#         newSkinCluster = \
#             mel.eval('newSkinCluster \"-tsb ' + bindMethod + weightLines[2] + '-omi true -rui false\"')[0]
#         cmds.rename(newSkinCluster, skinClusterName)

#         # get the current normalization and store it
#         # it will get re-applied after applying all the weights
#         normalization = cmds.getAttr(skinClusterName + '.nw')
#         # turn off the normalization to correctly apply the stored skin weights
#         cmds.setAttr((skinClusterName + '.nw'), 0)
#         # pruning the skin weights to zero is much faster
#         # than iterating through all components and setting them to 0
#         cmds.skinPercent(skinClusterName, shape, prw=100, nrm=0)

#     # allocate memory for the number of components to set
#     weights = eval(weightLines[len(weightLines) - 2])
#     # get the index of the last component stored in the weight list
#     maxIndex = weights[0]
#     cmds.select(skinClusterName, r=True)
#     cmdString = 'setAttr -s ' + str(maxIndex + 1) + ' \".wl\"'
#     OpenMaya.MGlobal.executeCommand(cmdString)

#     # --------------------------------------------------------------------------------
#     # apply the weight data
#     # --------------------------------------------------------------------------------

#     # timer for timing the read time without the smooth binding
#     # start = cmds.timerX()

#     for line in range(3, len(weightLines) - 1):

#         weights = eval(weightLines[line])
#         weightsNext = ''
#         # also get the next line for checking if the component changes
#         # but only if it's not the end of the list
#         if line < len(weightLines) - 2:
#             weightsNext = eval(weightLines[line + 1])
#         else:
#             weightsNext = weights
#             writeData = 1

#         compIndex = weights[0]

#         if specifics:
#             specificsList = specifics.split("_")
#             specificsList = [int(item) for item in specificsList]
#             if compIndex not in specificsList:
#                 continue
#         # --------------------------------------------------------------------------------
#         # construct the setAttr string
#         # i.e. setAttr -s 4 ".wl[9].w[0:3]"  0.0003 0.006 0.496 0.496
#         # --------------------------------------------------------------------------------

#         # start a new range
#         if inflStart == -1:
#             inflEnd = inflStart = weights[2]
#         else:
#             # if the current component is the next in line
#             if inflEnd == weights[2] - 1:
#                 inflEnd = weights[2]
#             # if influences were dropped because of zero weight
#             else:
#                 # fill the weight string inbetween with zeros
#                 for x in range(inflEnd + 1, weights[2]):
#                     weightString += '0 '
#                     setCount += 1
#                 inflEnd = weights[2]

#         # add the weight to the weight string
#         weightString += str(weights[3]) + ' '
#         # increase the number of weights to be set
#         setCount += 1

#         # if the next line is for the next index set the weights
#         if compIndex != weightsNext[0]:
#             writeData = 1

#         if writeData == 1:
#             # decide if a range or a single influence index is written
#             rangeString = ':' + str(inflEnd)
#             if inflEnd == inflStart:
#                 rangeString = ''

#             cmdString = 'setAttr -s ' + str(setCount) + ' \".weightList[' + str(compIndex) + '].weights[' + str(
#                 inflStart) + rangeString + ']\" ' + weightString
#             OpenMaya.MGlobal.executeCommand(cmdString)

#             # reset and start over
#             inflStart = inflEnd = -1
#             writeData = 0
#             setCount = 0
#             weightString = ''

#     cmds.setAttr((skinClusterName + '.nw'), normalization)

#     # doneTime = cmds.timerX(startTime = start)
#     # OpenMaya.MGlobal.displayInfo('%.02f seconds' % doneTime)

#     return 1


# def _writeSclsInfo(weightFile, obj, shape):
#     """Write the skinCluster node info to the file."""
#     weightFile.write(f"\n{shape}\n")
#     weightFile.write(f"{obj}_scls\n")

#     normalizeWeights = cmds.getAttr(f"{obj}_scls.normalizeWeights")
#     weightFile.write(f"-nw {normalizeWeights} ")

#     maxInfluences = cmds.getAttr(f"{obj}_scls.maxInfluences")
#     weightFile.write(f"-mi {maxInfluences} ")

#     dropoff = cmds.getAttr(f"{obj}_scls.dropoff")[0][0]
#     weightFile.write(f"-dr {dropoff}\n")
