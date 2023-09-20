"""Character API module."""


import rigsys.api.api_rig as api_rig


class Character:
    """Character class."""

    def __init__(self) -> None:
        """Initialize the character."""
        self.name = ""
        self.rigs: dict[str: api_rig.Rig] = {}
        self.version = "1.0.0"

    def build(self):
        """Build the character."""
        for rig in self.rigs.values():
            assert isinstance(rig, api_rig.Rig)
            rig.build()
