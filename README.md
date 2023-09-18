# Rig.Sys

Modular rigging system for Autodesk Maya.

- Character
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
