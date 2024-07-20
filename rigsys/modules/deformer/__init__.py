"""Deformer modules.

The following code dynamically imports all subclasses of DeformerModuleBase present in this directory. That way, you can
import any module in this directory and it will automatically be available in the rigging system.
"""

import glob
import importlib
import inspect
from os.path import basename, dirname, isfile, join

# This is the only line that needs to be changed per __init__.py file. Make sure to keep "as baseModule" at the end
from .deformerBase import DeformerModuleBase as baseModule

# Import all modules in the current directory
modules = glob.glob(join(dirname(__file__), "*.py"))
__all__ = [
    basename(f)[:-3] for f in modules if isfile(f) and not f.endswith("__init__.py")
]
for module in __all__:
    importlib.import_module("." + module, package=str(__name__))

# Get all the classes that inherit from baseModule
classes = {str(baseModule.__name__): baseModule}
for cls in baseModule.__subclasses__():
    classes[cls.__name__] = cls
    for subClass in cls.__subclasses__():
        classes[subClass.__name__] = subClass

# Import all the classes that inherit from baseModule
for cls in classes.values():
    classFilePath = inspect.getfile(cls)
    importStatement = f"from .{basename(classFilePath)[:-3]} import {cls.__name__}"
    exec(importStatement)

__all__ = list(classes.keys())

moduleTypes = classes.copy()
