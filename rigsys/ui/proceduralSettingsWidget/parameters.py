"""Variables for the settings widget."""

import re


def uiParam(obj, name, *args, **kwargs):
    """Create a uiParam object.

    Arguments:
        obj {object} -- The object to create the uiParam on.
        name {str} -- The name of the variable.
    """
    var = getattr(obj, name, None)
    if isinstance(var, bool):
        return _boolUIParam(name, *args, **kwargs)
    elif isinstance(var, int):
        return _intUIParameter(name, *args, **kwargs)
    elif isinstance(var, float):
        return _floatUIParameter(name, *args, **kwargs)
    elif isinstance(var, str):
        return _strUIParameter(name, *args, **kwargs)
    elif isinstance(var, list):
        return _listUIParameter(name, *args, **kwargs)
    elif isinstance(var, tuple):
        return _tupleUIParameter(name, *args, **kwargs)
    elif isinstance(var, dict):
        return _dictUIParameter(name, *args, **kwargs)


class _baseUIParam:
    """Base class for settings variables."""

    def __init__(self, name, label=None, defaultValue=None) -> None:
        self.name = name
        if label is None:
            self.label = " ".join([word.capitalize() for word in re.split(r"[\W_]+", name)])
        else:
            self.label = label

        self.defaultValue = defaultValue


class _boolUIParam(_baseUIParam):
    """Bool variable."""

    def __init__(self, name, displayName=None, defaultValue=None) -> None:
        """Initialize the variable."""
        super().__init__(name, displayName, defaultValue)


class _intUIParameter(_baseUIParam):
    def __init__(self, name, displayName=None, defaultValue=None, minValue=0, maxValue=10, isComboBox=False,
                 comboBoxItems=None):
        super(_intUIParameter, self).__init__(name, displayName, defaultValue)
        self.minValue = minValue
        self.maxValue = maxValue
        self.isComboBox = isComboBox
        self.comboBoxItems = comboBoxItems
        if self.comboBoxItems is None:
            self.comboBoxItems = [self.defaultValue]


class _floatUIParameter(_baseUIParam):
    def __init__(self, name, displayName=None, defaultValue=None, minValue=0.0, maxValue=10.0, stepSize=1.0,
                 isComboBox=False, comboBoxItems=None):
        super(_floatUIParameter, self).__init__(name, displayName, defaultValue)
        self.minValue = minValue
        self.maxValue = maxValue
        self.stepSize = stepSize
        self.isComboBox = isComboBox
        self.comboBoxItems = comboBoxItems
        if self.comboBoxItems is None:
            self.comboBoxItems = [self.defaultValue]


class _strUIParameter(_baseUIParam):
    def __init__(self, name, displayName=None, defaultValue=None, isCtrlStyle=False, isFile=False, isDir=False,
                 startDirectory="", isComboBox=False, comboBoxItems=None):
        super(_strUIParameter, self).__init__(name, displayName, defaultValue)
        self.isCtrlStyle = isCtrlStyle
        self.isFile = isFile
        self.isDir = isDir
        self.startDirectory = startDirectory
        self.isComboBox = isComboBox
        self.comboBoxItems = comboBoxItems
        if self.comboBoxItems is None:
            self.comboBoxItems = [self.defaultValue]


class _listUIParameter(_baseUIParam):
    def __init__(self, name, displayName=None, defaultValue=None, isVariableSize=False, hasListSettings=False,
                 objType=None, minItemsToDisplay=3, addSelected=False, isMultiVar=False, inVars=None):
        super(_listUIParameter, self).__init__(name, displayName, defaultValue)
        self.isVariableSize = isVariableSize
        self.hasListSettings = hasListSettings
        self.objType = objType
        self.minItemsToDisplay = minItemsToDisplay
        self.addSelected = addSelected
        self.isMultiVar = isMultiVar
        self.inVars = inVars


class _tupleUIParameter(_baseUIParam):
    def __init__(self, name, displayName=None, defaultValue=None):
        super(_tupleUIParameter, self).__init__(name, displayName, defaultValue)


class _dictUIParameter(_baseUIParam):
    def __init__(self, name, displayName=None, defaultValue=None, isVariableSize=False, keyHeader="Key",
                 valueHeader="Value", requireUniqueKeys=True):
        super(_dictUIParameter, self).__init__(name, displayName, defaultValue)
        self.isVariableSize = isVariableSize
        self.keyHeader = keyHeader
        self.valueHeader = valueHeader
        self.requireUniqueKeys = requireUniqueKeys


class _methodUIParameter(_baseUIParam):
    def __init__(self, name, displayName=None, defaultValue=None, args=None):
        super(_methodUIParameter, self).__init__(name, displayName, defaultValue)
        if args is None:
            args = []
        self.args = args
