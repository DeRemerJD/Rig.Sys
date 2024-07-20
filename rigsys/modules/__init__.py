"""Modules for rigging system."""

import rigsys.modules.deformer as deformer
import rigsys.modules.export as export
import rigsys.modules.motion as motion
import rigsys.modules.utility as utility

allModuleTypes = {}
allModuleTypes.update(motion.moduleTypes)
allModuleTypes.update(deformer.moduleTypes)
allModuleTypes.update(utility.moduleTypes)
allModuleTypes.update(export.moduleTypes)
