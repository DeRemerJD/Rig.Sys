"""Unit tests for the Root motion module."""


import unittest

import maya.cmds as cmds

import rigsys.api.api_rig as api_rig
from rigsys.modules.motion.Root import Root


class TestRootModule(unittest.TestCase):
    """Test the Root motion module."""

    def setUp(self) -> None:
        cmds.file(new=True, force=True)

        self.rig = api_rig.Rig()

        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_general(self):
        """Test that the module can be built."""
        self.rig.motionModules = {
            "Root": Root(
                self.rig,
                side="M",
                label="Root",
            ),
        }

        self.rig.build()
