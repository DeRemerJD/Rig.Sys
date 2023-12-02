# Plugs and Sockets

The module author defines the `module.plugs` and `module.sockets` dictionaries. These should be declared in the `__init__()` function with the key as the name of the plug/socket and the value as `None`. During the `run()` function (or `buildProxies()`/`buildModule()` functions), a node should be created and assigned properly in the plugs/sockets dictionary.

When creating a character, to properly do parenting, assign the `selectedPlug` and `selectedSocket` to choose which plug and socket to use for parenting. **Make sure that these match keys in the plug dictionary of the current module and socket dictionary of the parent module!** See [`exampleCharacter.py`](example/exampleCharacter.py) for an example of how to do this.
