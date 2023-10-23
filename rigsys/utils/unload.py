"""Utility function to unload modules for use in Maya."""


import logging
import sys

logger = logging.getLogger(__name__)

# if you have some packages that you often reload, you can put them here,
# and they will get reloaded if "packages" attribute is not explicitly stated
DEFAULT_RELOAD_PACKAGES = ["rigsys"]


def unloadPackages(silent=True, packages=None):
    """Unload all modules in the given packages.

    Args:
        silent (bool, optional): Whether to print out the modules that are being unloaded. Defaults to True.
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
