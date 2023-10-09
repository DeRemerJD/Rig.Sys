"""Test the ImportModel module."""

import os
import unittest

import maya.cmds as cmds

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
        cmds.file(new=True, force=True)

        self.rig = api_rig.Rig()

        self.resourcesFolder = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "resources")

        return super().setUp()

    def tearDown(self) -> None:
        """Tear down the test."""
        return super().tearDown()

    def test_importFBX(self):
        """Test the ImportModel module."""
        importFilePath = os.path.join(self.resourcesFolder, "cube.fbx")

        self.rig.utilityModules = {
            "ImportModel": utility.ImportModel(
                self.rig,
                "ImportModel",
                filePath=importFilePath,
            ),
        }

        self.rig.build()

        self.assertTrue(cmds.objExists("pCube1"))
