"""A widget to display and edit procedural settings."""

from . import version
from . import settingsWidget

VERSION = version.__version__
SettingsWidget = settingsWidget.SettingsWidget


__all__ = [
    "VERSION",
    "SettingsWidget",
]
