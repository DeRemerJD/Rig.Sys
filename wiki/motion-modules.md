# Motion Modules

Motion modules are used to SOMETHING. (TODO: finish this)

Motion modules have all the same properties as other modules, but with some extra functionality.

## Proxies

Proxies are some kind of node that is used to easily set positional and rotational values for rig nodes. (TODO: Jacob write this and make it sound less dumb)

Additionally, a motion module's `run()` function takes in extra arguments for working with proxies.

- `buildProxiesOnly`: If this is set to true, the module will only build proxies, and will not build the actual module. (It runs the `buildProxies()` function but not the `buildModule()` function, both of which are specific to motion modules.) This is useful for building proxy data for a module without actually building the module.
- `useSavedProxyData`: If this is set to true, the proxies will be positioned using saved proxy data, which will be passed in as the `proxyData` argument. Otherwise, proxies are positioned using their default locations as defined in the module. See [Working with proxies](working-with-proxies.md) for more information.
- `proxyData`: A dictionary of proxy data. This is read in from a JSON file and the relevant information is passed to each individual module. See [Working with proxies](working-with-proxies.md) for more information.

## Parenting, plugs, and sockets

Motion modules can be parented together and have a hierarchal relationship. For example, a hand may be parented to the wrist of an arm, which is parented to the shoulder of the spine, etc.

All motion modules have attributes for working with parenting.

- `parent`: A string representing the full name of the parent module. If this is set, the module will be parented to the parent module when the character is built.
- `_parentObject`: A direct reference to the parent module. This can be useful for accessing data directly from the parent module.
- `plugs`: A dictionary of plugs. See [Plugs and sockets](plugs-and-sockets.md) for more information.
- `sockets`: A dictionary of sockets. See [Plugs and sockets](plugs-and-sockets.md) for more information.
- `selectedPlug`: The plug of the child (current) module that will go into the parent's socket.
- `selectedParentSocket`: The socket of the parent module the child (current) module's plug will go into.
