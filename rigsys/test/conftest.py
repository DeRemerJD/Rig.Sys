import maya.standalone
import pytest

def pytest_sessionstart(session: pytest.Session):
    maya.standalone.initialize()

def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    maya.standalone.uninitialize()
