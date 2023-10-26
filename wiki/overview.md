# Rig.Sys

Rig.Sys is a modular rigging system for Autodesk Maya. Characters are saved as regular python files, which can also reference other data files (i.e. proxy positions, skin cluster data, etc.)

## Modules

Characters are made of groups of modules. The four types of modules are:

- Motion
- Utility
- Deformer
- Export

### Build order

Each module has a `buildOrder` attribute, which determines the order in which they are built. The build order is a number, and the lower the number, the earlier the module is built. For example, a module with a build order of 1000 will be built before a module with a build order of 2000. This means that the type of module has no bearing on when it is built. This allows for much more freedom when building characters, but also means that you need to be careful when setting build orders.

Additionally, the `build()` function in `rigsys.api.api_rig` can take a `buildLevel` argument, which will only build modules with a build order less than or equal to the build level. This is useful for debugging, or for building only a portion of a character.

### `run()`

Each module has a `run()` method, which is called when the character is built. This method is where you should put all of your code for building the module.

### Muting

Each module has an `isMuted` flag, which defaults to false. If this flag is set to true, the module will not be built when the character is built. This is useful for debugging, or for temporarily disabling a module.

### Sides and mirroring

All modules technically have side and mirroring information, although only motion and utility modules actually make use of these attributes.

### Dependencies

All modules have a `dependencies` dictionary. (TODO: finish this)
