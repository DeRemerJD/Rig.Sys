"""Run all tests in the test folder."""

import logging
import pytest
import sys

import maya.cmds as cmds

from pathlib import Path

from rigsys.utils.unload import unloadPackages, nukePycFiles


logger = logging.getLogger(__name__)


class StdOutWrapper:
    """Wrapper for stdout that fixes pytest capturing."""

    def __init__(self, stdout):
        """Initialize the wrapper."""
        self._stdout = stdout

    def __getattr__(self, item):
        """Get the attribute from the wrapped stdout."""
        if item == "isatty":
            return self.isatty
        else:
            return getattr(self._stdout, item)

    def isatty(self):
        """Return False."""
        return False


def fix_stdout():
    """Fix Maya stdout so that pytest can capture it."""
    sys.stdout = StdOutWrapper(sys.stdout)
    sys.stdout._stdout


def runTests(pattern="test_"):
    """Run all tests in the test folder."""
    unloadPackages(silent=False, packages=["rigsys"])
    nukePycFiles()

    test_path = Path(__file__).parent
    fix_stdout()

    pytest.main([test_path, "-k", pattern])

    cmds.file(new=True, force=True)


if __name__ == "__main__":
    runTests()
