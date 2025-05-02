import maya.cmds as cmds

###
'''
Retargeting tool. . . 
This tool matches xform data of a subject and target then keyframes it at the matching time slider based on range, and steps.
This tool assumes you will have a mocap skeleton, if you are retargetting based off a rig, skip to step 8B.
READ ME: 
    Subject : Animated Mocap Joint you want to copy.
    Target : Rig Control or Joint you want to match.
    Frame Range : [0, 120] represents starting frame, ending frame
    Frame Step : Which Frames in the Frame Range you want to copy. Every 1, 2, 12, ect. You pick. 
    Attributes : The attributes you want to keyframe. IE: translateX, translateY, yadda yadda... 
    World Space : By default, set to True, you should not need to change this. 
    Allowed Attributes : Acts as a checklist so you cant break anything. 
    Pose Match Frame : The Frame where you manually set the pose of the rig to match the default pose of the Mocap Skeleton. 

HOW TO USE KEYFRAME DATA RETARGET
1 ) Copy and paste this entire code base into your Maya Python Window in the script editor.

2 ) Copy and paste this below the code you just copied for EACH joint you want to retarget.

retargetting = KeyframeData(subject="MOCAP JOINT", target="RIG CONTROL", 
                frameRange=[0, 120], frameStep=12, worldSpace=True, 
                attributes=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ'],
                poseMatchFrame=-1)
retargetting.runRetarget()

3 ) Replace "MOCAP JOINT" (keep the " marks) with the joint you want to copy animation from 
    and replace "RIG CONTROL" with the control you want to be keyframed. 

4 ) Change the frameRange and frameStep to whatever you want. You could bake the animation every frame or every 12, 24, 8, whatever.
    I have it set to 12 by default. 

5 ) Change which attributes you want to keyframe. You can copy the below section if you have a typo somewhere and replace the whole section.

    attributes=['translateX', 'translateY', 'translateZ', 'rotateX', 'rotateY', 'rotateZ', 'scaleX', 'scaleY', 'scaleZ']

6 ) Change the poseMatchFrame to whatever frame you want to manually keyframe a pose match. (More on this later.) by default its 
    set to frame -1

7 ) IN MAYA; out of the script editor, goto the frame that matches your poseMatchFrame. By default this is -1.
    This should be a frame with no animation keyframed on it. 

8A ) IF you have a mocap skeleton...
        Select the root joint of the mocap skeleton.
        Copy and paste the below code into the MEL line in MAYA, hit Enter.
            select-hi
        Then zero out all 3 rotation attributes in the channel box. Keyframe.
        This will keyframe the Mocap skeleton in the default pose (probably T) at the poseMatchFrame.

8B ) IF you have a rig (that you want to copy animation from)...
        Select all controls, zero them out. Keyframe.

9 ) Now, at the same poseMatchFrame manually move your rig into a pose that ROUGHLY matches the Mocap skeleton. 
        Do note, they do not need to be of similar size. Just a matching A or T pose will do. 

        Then Keyframe the rig. 

10 ) Now you should have both the RIG and the MOCAP SKELETON keyframed in a matching pose at the poseMatchFrame. (by default -1)
        Simply select all the code in this file and hit the blue play button to the top of the screen.
        (not the dual play button, the singular)

11 ) This has baked the animation retarget to the RIG. Congrats, youre a programmer!

EDITORS NOTE: I got an art degree and do this shit for a living fml

'''
###
# Do Not Copy
class KeyframeData():
    """ Keyframe master class for all keyframe data """
    def __init__(self, subject: str = None, target: str = None, 
                frameRange: list = [0, 120] , frameStep: int = 24, 
                attributes: list = ['translateX', 'translateY', 'translateZ',
                                    'rotateX', 'rotateY', 'rotateZ',
                                    'scaleX', 'scaleY', 'scaleZ'],
                worldSpace: bool = True,
                allowedAttributes: tuple = ['translateX', 'translateY', 'translateZ',
                                            'rotateX', 'rotateY', 'rotateZ',
                                            'scaleX', 'scaleY', 'scaleZ'],
                poseMatchFrame: int = -1):
        self.subject = subject
        self.target = target
        self.frameRange = frameRange
        self.frameStep = frameStep
        self.attributes = attributes
        self.worldSpace = worldSpace
        self.allowedAttributes = allowedAttributes
        self.poseMatchFrame = poseMatchFrame
        
    def retargetMatch(self, subject, target,
                        frameRange, frameStep,
                        attributes, worldSpace,
                        poseMatchFrame):
        ### Create Frame
        # Safety checks
        if subject != None: # Check if subject is not None.
            if not cmds.objExists(subject): # Check if subject exists.
                print("Make sure there are not multiple objects of the same name in the scene.")
                cmds.error(f"{subject} does not exists, please check spelling.")
        else: # Check if subject is None
            cmds.error("Subject is None, provide a subject.")
        if target != None: # Check if target is not None.
            if not cmds.objExists(target): # Check if target exists.
                print("Make sure there are not multiple objects of the same name in the scene.")
                cmds.error(f"{target} does not exists, please check spelling.")
        else: # Check if target is None.
            cmds.error("Target is None, provide a target.")
        failed = [] # Used for tracking printing any attributes not allowed / misspelled. 
        for i in attributes: # Check if attributes are spelled correctly / are permitted to be keyframed. 
            if i not in self.allowedAttributes:
                failed.append(i)
        if len(failed) > 0:
            cmds.error(f"The following keyframe attributes are not allowed / incorrect. Check spelling. . . {failed}.")

        # Set frame to pose match frame. . . 
        cmds.currentTime(poseMatchFrame)
        # Create two nodes for tracking data.        
        pm = cmds.createNode("transform", n=f"{target}_ZeroOffset_PoseMatch")
        tpm = cmds.createNode("transform", n=f"{target}_TrackingMatch", p=pm)
        nodes = [pm, tpm] # List for deleting later... 

        # Move pm to target position / rotation / scale
        cmds.xform(pm, ws=True, m=cmds.xform(target, q=True, ws=True, m=True))
        # Determine if we need point, orient or scale constraints for offsets. . .
        constraints = [] # List of constraints for deleting later.
        pc = cmds.pointConstraint(subject, tpm, mo=1, n=f"{tpm}_pc")[0]
        constraints.append(pc)
        oc = cmds.orientConstraint(subject, tpm, mo=1, n=f"{tpm}_pc")[0]
        cmds.setAttr(f"{oc}.interpType", 2)
        constraints.append(oc)
        sc = cmds.scaleConstraint(subject, tpm, mo=1, n=f"{tpm}_sc")[0]
        constraints.append(sc)
        
        for frame in range(frameRange[0], frameRange[1], frameStep): # Frame range and frame step parse
            if frame > frameRange[1]: # Dont keyframe beyond the frame range if frame step isnt divisible by frame range
                break # Die Die Die!

            cmds.currentTime(frame) # Set frame to frame step
            cmds.xform(target, ws=worldSpace, m=cmds.xform(tpm, q=True, ws=worldSpace, m=True)) # Apply TPM matrix to target
            for attr in attributes: # Parse Attributes in list
                cmds.setKeyframe(target, attribute=attr, time=frame) # Keyframe at current value

        cmds.delete(constraints)
        cmds.delete(nodes)


    def runRetarget(self):
        self.retargetMatch(subject=self.subject,
                           target=self.target,
                           frameRange=self.frameRange,
                           frameStep=self.frameStep,
                           attributes=self.attributes,
                           worldSpace=self.worldSpace,
                           poseMatchFrame=self.poseMatchFrame)

