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

### Parenting

## Saving and loading proxies

## Adding deformers

## Running custom python code

## Exporting
