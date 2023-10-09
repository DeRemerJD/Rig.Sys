# Rig.Sys

Modular rigging system for Autodesk Maya.

- Rigs
  - Proxies
  - Motion Modules
    - Build order (int)
    - Proxies built (bool)
    - Module built (bool)
  - Deform Modules
  - Utility Modules
  - Export Modules
  - Python Code

Characters are stored as Python files that subclass from the `Character` class. Data such as proxy translations and skin
weights are stored in JSON files.

## Unit testing

The rigsys package provides unit tests and a test runner that needs to be run within Maya. Copy and paste the following code into the script editor:

```python
import rigsys.utils.unload as unload
unload.unloadPackages(packages=["rigsys"])

import rigsys.test.testRunner as testRunner

testRunner.runTests()
```
