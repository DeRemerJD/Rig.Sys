"""Utility function to unload modules for use in Maya."""


import os
import shutil
import logging
import sys

logger = logging.getLogger(__name__)

# if you have some packages that you often reload, you can put them here,
# and they will get reloaded if "packages" attribute is not explicitly stated
DEFAULT_RELOAD_PACKAGES = ["rigsys"]


def unloadPackages(silent=True, packages=None):
    """Unload all modules in the given packages.

    Args:
        silent (bool, optional): Whether to log the modules that are being unloaded. Defaults to True.
        packages (list, optional): List of packages to unload. Defaults to "rigsys".
    """
    if packages is None:
        packages = DEFAULT_RELOAD_PACKAGES

    # construct reload list
    reloadList = []
    for sysModule in sys.modules.keys():
        for package in packages:
            if sysModule.startswith(package):
                reloadList.append(sysModule)

    # unload everything
    for moduleToReload in reloadList:
        try:
            if sys.modules[moduleToReload] is not None:
                del (sys.modules[moduleToReload])
                if not silent:
                    logger.debug(f"Unloaded: {moduleToReload}")

        except KeyError:
            if silent:
                pass
            else:
                logger.warning(f"Could not unload: {moduleToReload}")


def nukePycFiles(folderPath=None, verbose=False):
    """Remove all .pyc files in a folder.

    Args:
        folderPath: The path to the folder to remove the .pyc files from.
        verbose: If True, log the names of the files removed.
    """
    if folderPath is None:
        folderPath = os.path.join(os.path.dirname(__file__), os.pardir)

    for root, dirs, files in os.walk(folderPath):
        for file in files:
            if file.endswith(".pyc") or file.endswith(".bak"):
                os.remove(os.path.join(root, file))
                if verbose:
                    logger.info(f"Removed {os.path.abspath(os.path.join(root, file))}")
        for dirName in dirs:
            if dirName.startswith("__pycache__") or dirName.startswith(".pytest_cache"):
                shutil.rmtree(os.path.join(root, dirName))
                if verbose:
                    logger.info(f"Removed {os.path.abspath(os.path.join(root, dirName))}")
