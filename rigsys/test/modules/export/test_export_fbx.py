"""Unit tests for the FBX Export module."""

import os
import unittest

import rigsys.api.api_rig as api_rig
import rigsys.modules.export as export
import rigsys.modules.utility as utility
import rigsys.modules.export.fbxExport as fbxExportModule


import maya.cmds as cmds


class TestFBXExport(unittest.TestCase):
    """Test the FBX Export module."""

    def setUp(self) -> None:
        cmds.file(new=True, force=True)

        self.rig = api_rig.Rig()

        self.resourcesFolder = os.path.join(os.path.dirname(__file__), os.pardir, os.pardir, "resources")
        self.exportFilePath = os.path.abspath(os.path.join(self.resourcesFolder, "test.fbx"))

        if os.path.exists(self.exportFilePath):
            os.remove(self.exportFilePath)

        return super().setUp()

    def tearDown(self) -> None:
        if os.path.exists(self.exportFilePath):
            os.remove(self.exportFilePath)

        return super().tearDown()

    def test_general(self):
        """Test that the module can be built."""
        importFilePath = os.path.join(self.resourcesFolder, "cube.fbx")
        self.rig.utilityModules = {
            "ImportModel": utility.ImportModel(
                self.rig,
                "ImportModel",
                filePath=importFilePath,
            ),
        }
        self.rig.exportModules = {
            "FBXExport": export.FBXExport(
                self.rig,
                exportPath=self.exportFilePath,
                exportAll=True,
            ),
        }

        self.rig.build()

        assert os.path.exists(self.exportFilePath)

        cmds.file(new=True, force=True)

        # Open the file to make sure the cube exists
        cmds.file(self.exportFilePath, o=True, force=True)

        self.assertTrue(cmds.objExists("pCube1"))

    def test_exportSelected(self):
        """Test the export selected flag."""
        importCubeFilePath = os.path.join(self.resourcesFolder, "cube.fbx")
        importSphereFilePath = os.path.join(self.resourcesFolder, "sphere.fbx")
        self.rig.utilityModules = {
            "ImportCube": utility.ImportModel(
                self.rig,
                "ImportCube",
                filePath=importCubeFilePath,
            ),
            "ImportSphere": utility.ImportModel(
                self.rig,
                "ImportSphere",
                filePath=importSphereFilePath,
            ),
        }
        self.rig.exportModules = {
            "FBXExport": fbxExportModule.FBXExport(
                self.rig,
                exportPath=self.exportFilePath,
                exportSelected=True,
                nodesToExport=["pCube1"],
            ),
        }

        self.rig.build()

        self.assertTrue(cmds.objExists("pCube1"))
        self.assertTrue(cmds.objExists("pSphere1"))

        assert os.path.exists(self.exportFilePath)

        cmds.file(new=True, force=True)

        # Open the file to make sure the cube exists
        cmds.file(self.exportFilePath, o=True, force=True)

        self.assertTrue(cmds.objExists("pCube1"))
        self.assertFalse(cmds.objExists("pSphere1"))

    def test_exportAll(self):
        """Test the export all flag."""
        importCubeFilePath = os.path.join(self.resourcesFolder, "cube.fbx")
        importSphereFilePath = os.path.join(self.resourcesFolder, "sphere.fbx")
        self.rig.utilityModules = {
            "ImportCube": utility.ImportModel(
                self.rig,
                "ImportCube",
                filePath=importCubeFilePath,
            ),
            "ImportSphere": utility.ImportModel(
                self.rig,
                "ImportSphere",
                filePath=importSphereFilePath,
            ),
        }
        self.rig.exportModules = {
            "FBXExport": fbxExportModule.FBXExport(
                self.rig,
                exportPath=self.exportFilePath,
                exportAll=True,
            ),
        }

        self.rig.build()

        self.assertTrue(cmds.objExists("pCube1"))
        self.assertTrue(cmds.objExists("pSphere1"))

        assert os.path.exists(self.exportFilePath)

        cmds.file(new=True, force=True)

        # Open the file to make sure the cube exists
        cmds.file(self.exportFilePath, o=True, force=True)

        self.assertTrue(cmds.objExists("pCube1"))
        self.assertTrue(cmds.objExists("pSphere1"))

    def test_isMuted(self):
        self.rig.exportModules = {
            "FBXExport": fbxExportModule.FBXExport(
                self.rig,
                exportPath=self.exportFilePath,
                exportAll=True,
                isMuted=True,
            ),
        }

        self.rig.build()

        assert not os.path.exists(self.exportFilePath)
