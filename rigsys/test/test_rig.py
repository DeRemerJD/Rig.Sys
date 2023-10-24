"""api_rig unit tests."""


import unittest

import rigsys.api.api_rig as api_rig
import rigsys.modules.motion as motion
import rigsys.modules.utility as utilityModules


class TestRig(unittest.TestCase):
    """Test the Rig class."""

    def setUp(self) -> None:
        """Set up the test."""
        return super().setUp()

    def tearDown(self) -> None:
        """Tear down the test."""
        return super().tearDown()

    def test_character(self):
        """Test the Character class."""
        rig = api_rig.Rig()

        rig.motionModules = {
            "M_Root": motion.Root(
                rig,
                side="M",
                label="Root",
            ),
            "M_Spine": motion.TestMotionModule(
                rig,
                side="M",
                label="Spine",
                parent="M_Root",
            ),
            "L_Arm": motion.TestMotionModule(
                rig,
                side="L",
                label="Arm",
                mirror=True,
                parent="M_Spine",
            ),
            "L_Hand": motion.TestMotionModule(
                rig,
                side="L",
                label="Hand",
                mirror=True,
                parent="L_Arm",
            ),
            "L_Hand_2": motion.TestMotionModule(
                rig,
                side="L",
                label="Hand_2",
                mirror=True,
                parent="L_Arm",
            ),
            "L_Watch": motion.TestMotionModule(
                rig,
                side="L",
                label="Watch",
                parent="L_Arm",
            ),
        }

        rig.build(usedSavedProxyData=False)
