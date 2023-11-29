"""Modular rigging system for Autodesk Maya."""


import logging

from rigsys.api.api_rig import Rig

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

__all__ = ["Rig"]
