"""Character API module."""


import rigsys.api.api_rig as api_rig


class Character:
    """Character class."""

    def __init__(self) -> None:
        """Initialize the character."""
        self.name = ""
        self.rigs = {}
        self.version = "1.0.0"
