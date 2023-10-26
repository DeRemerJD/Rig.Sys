# Getting started

## Installation

See [Installation](installation.md) for more information.

## Examples

See the `examples` folder of this repository for examples of how to use Rig.Sys.

## Creating your first character

After you've installed Rig.Sys, you can create your first character. To do this, you'll need to create a new Python file. This file will contain the code for your character. You can name it whatever you want, but for this example, we'll name it `exampleCharacter.py`.

At the top of the file, import rigsys, maya.cmds, and any other modules you need.

```python
import rigsys
import maya.cmds as cmds
```

Next, create a class that subclasses from `rigsys.Rig`. This class will contain all of the code for your character.

```python
class ExampleCharacter(rigsys.Rig):
    pass
```

In the `__init__()` function of the character, call the `__init__()` function of the parent class, and pass the name of your character. We'll also initialize dictionaries for all our module types.

```python
class ExampleCharacter(rigsys.Rig):
    def __init__(self):
        super().__init__(name="ExampleCharacter")

        self.motionModules = {}
        self.utilityModules = {}
        self.deformerModules = {}
        self.exportModules = {}
```

At the bottom of your file, create an instance of your character class and call the `build()` method.

```python
if __name__ == "__main__":
    character = ExampleCharacter()
    character.build()
```

At this point, your total file should look like this:

```python
import rigsys
import maya.cmds as cmds


class ExampleCharacter(rigsys.Rig):
    def __init__(self):
        super().__init__(name="ExampleCharacter")

        self.motionModules = {}
        self.utilityModules = {}
        self.deformerModules = {}
        self.exportModules = {}


if __name__ == "__main__":
    character = ExampleCharacter()
    character.build()
```

If you open this script in the Maya script editor and run it, you should see a character named `ExampleCharacter` created in your scene. However, this is pretty boring. Let's add some modules to our character.

## Importing a model

Let's start with importing a model. To do this, we'll add the `ImportModel` utility module to the `utilityModules` dictionary in the `__init__()` function. We'll need to import `rigsys.modules.utility` to access the `ImportModel` class.

```python
import rigsys
import rigsys.modules.utility as utility
import maya.cmds as cmds


class ExampleCharacter(rigsys.Rig):
    def __init__(self):
        super().__init__(name="ExampleCharacter")

        self.motionModules = {}
        self.utilityModules = {
            "ImportModel": utility.ImportModel(
                self,
                filePath="C:/path/to/model.mb",
            ),
        }
        self.deformerModules = {}
        self.exportModules = {}


if __name__ == "__main__":
    character = ExampleCharacter()
    character.build()
```

## Adding motion modules

_Coming soon_

### Parenting

_Coming soon_

## Saving and loading proxy transforms

Run the python file to build the character and manually move some of the proxies around.

At the bottom of our file, let's declare a path to the proxy save file. We'll comment out the build step for now, since we don't want to build the character yet and add in a call to `saveProxyTransformations()`, passing in the path to the proxy save file.

```python
if __name__ == "__main__":
    proxyDataFile = "C:/path/to/proxyData.json"

    character = ExampleCharacter()
    # character.build()
    character.saveProxyTransformations(proxyDataFile)
```

You should see a file called `proxyData.json` created in the specified directory. If you open it, you should see a json object with the names of the proxies and their world space transformations.

To load the proxy data, we'll need to add a few arguments to the `build()` method. We'll set `useSavedProxyData` to `True` and pass in the path to the proxy save file. We'll also comment out the call to `saveProxyTransformations()`.

```python
if __name__ == "__main__":
    proxyDataFile = "C:/path/to/proxyData.json"

    character = ExampleCharacter()
    character.build(useSavedProxyData=True, proxyDataFile=proxyDataFile)
    # character.saveProxyTransformations(proxyDataFile)
```

If you build the character again, you should see that the proxies are built in the same positions as they were when you saved the proxy data. Whenever you need to reposition the proxies, comment out the call to `build()` and uncomment the call to `saveProxyTransformations()`. Then, build the character again.

## Adding deformers

_Coming soon_

## Running custom python code

With the help of the `PythonCode` module, we can run a python script at any point of the build process. To start, let's create a simple python script that creates a sphere in the scene.

```python
import maya.cmds as cmds

cmds.polySphere()
```

We'll save this as `create_sphere.py`, and reference it in our character file. We can set the `buildOrder` variable to force it to run before or after other modules.

```python
self.utilityModules = {
    ...
    "Python_CreateSphere": utility.PythonCode(
        self,
        filePath="C:/path/to/create_sphere.py",
        buildOrder=0,  # Run first
    ),
}
```

When we build our character, we should see a sphere created in the scene!

## Exporting

Once our character is fully built, we may want to automatically send it to a deliverable folder for the animator to use. We can do this with the `Export` module. Let's add it to our character file.

```python
import rigsys.modules.export as export

self.exportModules = {
    "MBExport": export.MBExport(
        self,
        exportPath="C:/path/to/character.mb",
        exportAll=True,
    ),
}
```

Let's say we also want to batch out the skeleton of our character to a separate FBX file. We can do this by adding another `Export` module to our character file and specifying what nodes to export.

```python
self.exportModules = {
    "MBExport": export.MBExport(
        self,
        exportPath="C:/path/to/character.mb",
        exportAll=True,
    ),
    "FBXSkeletonExport": export.FBXExport(
        self,
        exportPath="C:/path/to/character_skeleton.fbx",
        exportSelected=True,
        nodesToExport=["skeleton"],
    ),
}
```
