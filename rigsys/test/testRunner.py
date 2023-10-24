"""Run all tests in the test folder."""

import os
import pytest

from rigsys.utils.unload import unloadPackages, nukePycFiles


def runTests(pattern="test_"):
    """Run all tests in the test folder."""
    unloadPackages(silent=False, packages=["rigsys"])
    nukePycFiles()

    testPath = os.path.dirname(__file__)

    pytest.main([testPath, "-k", pattern])


if __name__ == "__main__":
    runTests()
