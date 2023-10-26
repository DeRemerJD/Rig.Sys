# Module authoring

Rig.sys is designed to be extensible by individual riggers, and users are encouraged to write their own modules to suit their needs. This page will go over the basics of writing your own modules. (If you have a module you particularly like, feel free to submit a pull request to have it added to the main rig.sys package!)

The first step is determining what type of module you want to write. There are four types of modules:

- Motion
- Utility
- Deformer
- Export

However, you can also write your own custom module types by inheriting from the `ModuleBase` class. This is useful if you want to write a module that doesn't fit into one of the four existing categories.

## Principles to keep in mind when writing modules

### Modules should be self-contained

A module should be able to build by itself, without any other modules. For example, a hand module should not need an arm module to be built first to work properly.

### Modules should parent all created nodes under the module group

This is important for keeping the rig organized. If a module creates a node, it should be parented under the module group.
