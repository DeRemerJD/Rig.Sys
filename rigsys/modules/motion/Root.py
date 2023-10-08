"""World Root Motion Module."""


import rigsys.modules.motion.motionBase as motionBase
import rigsys.lib.ctrl as ctrlCrv
import maya.cmds as cmds


class Root(motionBase.MotionModuleBase):
    """Root Motion Module."""

    def __init__(self, *args, **kwargs) -> None:
        """Initialize the module."""

        # Public editables
        self.name = "Root"
        self.addOffset = True


        # Proxy?
        self.proxies = {
            "Root": rsProxy(blahblahblah, position=[0,0,0], rotation=[0,0,0]),
        }

        super().__init__(args, kwargs)

    def run(self) -> None:
        """Run the module."""
        # TODO: Implement
        
        # Build overall structure
        proxyPosition = self.proxies["Root"].position

        # Structure
        rootPar = cmds.createNode("transform", n=side+label+self.name+"_grp")
        rootCtrl = cmds.createNode("transform", n=side+label+self.name+"_CTRL")
        cmds.parent(rootCtrl, rootPar)
        rootCtrlObj = ctrlCrv.Ctrl(node=rootCtrl, shape="circle")
        rootCtrlObj.giveCtrlShape()
        if self.addOffset:
            offsetPar = cmds.createNode("transform", n=side+label+self.name+"_grp")
            offsetCtrl = cmds.createNode("transform", n=side+label+self.name+"_CTRL")
            cmds.parent(offsetCtrl, offsetPar)
            cmds.parent(offsetPar, rootCtrl)
            offsetCtrlObj = ctrlCrv.Ctrl(node=offsetCtrl, shape="circle")
            offsetCtrlObj.giveCtrlShape()
        cmds.xform(rootPar, ws=True, t=proxyPosition)


