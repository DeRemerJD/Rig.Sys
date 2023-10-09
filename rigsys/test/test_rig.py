"""api_rig unit tests."""


import unittest

import rigsys.api.api_rig as api_rig
import rigsys.modules.motion as motionModules
import rigsys.modules.utility as utilityModules


class TestRig(unittest.TestCase):
    """Test the Rig class."""

    def setUp(self) -> None:
        """Set up the test."""
        return super().setUp()

    def tearDown(self) -> None:
        """Tear down the test."""
        return super().tearDown()

    # def test_character(self):
    #     """Test the Character class."""
    #     rig = api_rig.Rig()

    #     rig.motionModules = {
    #         "IK": motionModules.IK(self),
    #         "FK": motionModules.FK(self),
    #         "Floating": motionModules.Floating(self),
    #     }

    #     rig.utilityModules = {
    #         "ImportModel": utilityModules.ImportModel(self),
    #         "BindJoints": utilityModules.BindJoints(self),
    #     }

    #     rig.build()
