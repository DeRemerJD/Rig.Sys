# Utility modules

Utility modules are somewhat of a catch-all for modules that don't fit into the other categories. They are used for things like parenting, mirroring, and other miscellaneous tasks. As such, they are given access to side and mirroring information, but not parenting information.

Utility modules are especially good at running at any point during the build process. A utility module may be used to import a model at the very beginning of a build, parent motion modules together after they have been built, or clean up the scene before export.
