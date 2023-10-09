"""Test the ImportModel module."""

import os
import unittest

import rigsys.api.api_rig as api_rig
import rigsys.modules.utility as utility


"""Things to test:
- Single model import
- Multiple in same rig with same group
- Multiple in same rig with different group
- With and without underGroup
- Invalid filepath
"""


class TestImportModel(unittest.TestCase):
    """Test the ImportModel class."""

    def setUp(self) -> None:
        """Set up the test."""
        return super().setUp()

    def tearDown(self) -> None:
        """Tear down the test."""
        return super().tearDown()

    def test_importModel(self):
        """Test the ImportModel module."""
        rig = api_rig.Rig()
        rig.utilityModules = {"ImportModel": utility.ImportModel(rig, "ImportModel", filePath="test/data/test.ma")}
