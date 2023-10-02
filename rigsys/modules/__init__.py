"""Modules for rigging system."""

import rigsys.modules.motion as motion
import rigsys.modules.deformer as deformer
import rigsys.modules.utility as utility
import rigsys.modules.export as export


allModuleTypes = {}
allModuleTypes.update(motion.moduleTypes)
allModuleTypes.update(deformer.moduleTypes)
allModuleTypes.update(utility.moduleTypes)
allModuleTypes.update(export.moduleTypes)
