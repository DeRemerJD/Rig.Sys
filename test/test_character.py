"""api_character unit tests."""


import unittest

import rigsys.api.api_character as api_character
import rigsys.api.api_rig as api_rig
import rigsys.modules.motion as motionModules
import rigsys.modules.utility as utilityModules


class TestCharacter(unittest.TestCase):
    """Test the Character class."""

    def setUp(self) -> None:
        """Set up the test."""
        return super().setUp()

    def tearDown(self) -> None:
        """Tear down the test."""
        return super().tearDown()

    def test_character(self):
        """Test the Character class."""
        character = api_character.Character()
        self.assertIsInstance(character, api_character.Character)

        mainRig = api_rig.Rig()
        character.rigs["main"] = mainRig

        mainRig.motionModules = {
            "IK": motionModules.IK(),
            "FK": motionModules.FK(),
            "Floating": motionModules.Floating(),
        }

        mainRig.utilityModules = {
            "ImportModel": utilityModules.ImportModel(),
            "BindJoints": utilityModules.BindJoints(),
        }

        character.build()
