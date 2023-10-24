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

## Motion module parenting

Motion modules can be parented to other motion modules. This is done by setting the `parent` attribute on the module to the name of the parent module. If the name of the parent module is not found, an error will be raised when the character is built.

**IMPORTANT: Parent modules will not inherently be built before children.** If a child module depends on something in the parent module being built, you need to make sure the parent module is built first by setting the `buildOrder` attribute.

## Motion module mirroring

To set a motion module to be mirrored, set the `mirror` attribute to `True` on the module. This will cause the module to be mirrored when the character is built.

**IMPORTANT: Children of a mirrored module are not automatically mirrored,** the user must set the `mirror` attribute on each child module they wish to be mirrored.

Example:

- `M_Spine` (not mirrored)
  - `L_Arm` (mirrored)
    - `L_Hand` (mirrored)
    - `L_Watch` (not mirrored)
  - `R_Arm` (created by mirroring `L_Arm`)
    - `R_Hand` (created by mirroring `L_Hand`)

## Unit testing

Unit testing for rigsys is done using [pytest](https://docs.pytest.org/en/7.4.x/). You can install it automatically by running the following script within Maya.

```python
import subprocess
import sys

mayapyExecutable = os.path.dirname(sys.executable)
mayapyExecutable = os.path.join(mayapyExecutable, "mayapy.exe")

def pipInstallPackage(packageName) -> bool:
    """Use pip to install a package."""
    command = [
        mayapyExecutable, "-m", "pip", "install", "--upgrade", "--force-reinstall", packageName
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode == 0:
        print(result.stdout)
        return True
    else:
        print(result.stderr)
        return False
        
pipInstallPackage("pytest")
```

The rigsys package provides unit tests and a test runner that needs to be run within Maya. Copy and paste the following code into the script editor:

```python
import rigsys.utils.unload as unload
unload.unloadPackages(packages=["rigsys"])

import rigsys.test.testRunner as testRunner

testRunner.runTests()
```
