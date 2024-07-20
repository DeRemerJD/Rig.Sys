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

The actual parenting will be done by the `MotionModuleParenting` utility module. This module searches for motion modules that have parenting information provided and performs the parenting in Maya. (See the [Plugs and Sockets](#plugs-and-sockets) section below.) If you don't include one, one will be added automatically. You may want to add this module manually if you want to control the order in which the parenting is done. It defaults, like all utility modules, to building at order 3000.

### Plugs and Sockets

The module author defines the `module.plugs` and `module.sockets` dictionaries. These should be declared in the `__init__()` function with the key as the name of the plug/socket and the value as `None`. During the `run()` function (or `buildProxies()`/`buildModule()` functions), a node should be created and assigned properly in the plugs/sockets dictionary.

When creating a character, to properly do parenting, assign the `selectedPlug` and `selectedSocket` to choose which plug and socket to use for parenting. **Make sure that these match keys in the plug dictionary of the current module and socket dictionary of the parent module!** See [`exampleCharacter.py`](example/exampleCharacter.py) for an example of how to do this.

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

## Proxy transformation saving and loading

Proxy transformations (world space translations and rotations) are saved in a user-specified json file.

To save proxy data to a file, build a character, transform proxies as desired, then call the character's `saveProxyTransformations()` method. This takes in a file path to save the data to.

To load proxy data from a file, use the `useSavedProxyData` and `proxyDataFile` arguments in the `build()` method. `useSavedProxyData` defaults to False and means that proxies will be built using their default transformation values.

The overall workflow might look like this:

Build the character

```python
character = ExampleCharacter()
character.build()
```

Then, manually transform the proxies as desired and save their positions.

```python
character = ExampleCharacter()
proxyDataFile = "C:/path/to/proxyData.json"

character.saveProxyTransformations(proxyDataFile)
```

Then, load the proxy data and build the character again.

```python
character = ExampleCharacter()
proxyDataFile = "C:/path/to/proxyData.json"

character.build(useSavedProxyData=True, proxyDataFile=proxyDataFile)
```

I usually like to have both the save and build commands in the same file, which I can toggle on and off by commenting/uncommenting the lines.

```python
character = ExampleCharacter()
proxyDataFile = "C:/path/to/proxyData.json"

character.build(usedSavedProxyData=True, proxyDataFile=proxyDataFile)
# character.saveProxyTransformations(proxyDataFile)
```

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
unload.nukePycFiles()

import rigsys.test.testRunner as testRunner

testRunner.runTests()
```

You can also provide a pattern to the `runTests()` function to only run tests that match the pattern. For example, to only run tests that match the pattern `test_rig`, you would run the following:

```python
testRunner.runTests(pattern="test_rig")
```

Based on the naming convention of the tests, you can single out specific types of modules (i.e. "test_export" or "test_motion") to run all tests of that module type.
