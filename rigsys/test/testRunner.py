"""Run all tests in the test folder."""

import io
import os
from unittest import TestLoader, TextTestRunner


def runTests(pattern="test_*.py"):
    """Run all tests in the test folder."""
    testPath = os.path.dirname(__file__)

    testSuite = TestLoader().discover(testPath, pattern=pattern)
    stream = io.StringIO()
    runner = TextTestRunner(stream=stream, verbosity=2)
    runner.run(testSuite)
    print("\n\n============================== RESULTS: ==============================\n")
    print(stream.getvalue())


if __name__ == "__main__":
    runTests()
