"""api_character unit tests."""


import unittest
import rigsys.api.api_character as api_character


class TestCharacter(unittest.TestCase):
    """Test the Character class."""

    def test_character(self):
        """Test the Character class."""
        character = api_character.Character()
        self.assertIsInstance(character, api_character.Character)
