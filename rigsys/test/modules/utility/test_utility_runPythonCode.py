"""Test the PythonCode module."""


import os
import unittest

import maya.cmds as cmds

import rigsys.modules.utility as utility
from rigsys import Rig


class TestPythonCode(unittest.TestCase):
    """Test the PythonCode module."""

    def setUp(self) -> None:
        cmds.file(new=True, force=True)

        self.rig = Rig()

        self.resourcesFolder = os.path.join(
            os.path.dirname(__file__), os.pardir, os.pardir, "resources"
        )

        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_general(self):
        """Ensure the module runs properly."""
        pythonFilePath = os.path.join(self.resourcesFolder, "create_sphere.py")

        self.rig.utilityModules = {
            "PythonCode": utility.PythonCode(
                self.rig,
                pythonFilePath,
            )
        }

        self.rig.build()

        self.assertTrue(cmds.objExists("pSphere1"))

    def test_errorHandling(self):
        """Ensure the module handles errors properly."""
        pythonFilePath = os.path.join(self.resourcesFolder, "invalid_python.py")

        self.rig.utilityModules = {
            "PythonCode": utility.PythonCode(
                self.rig,
                pythonFilePath,
            )
        }

        with self.assertRaises(IndentationError):
            self.rig.build()
