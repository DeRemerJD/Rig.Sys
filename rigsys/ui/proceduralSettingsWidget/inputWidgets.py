"""Input widgets for procedural settings widget."""

from PySide2 import QtWidgets, QtCore, QtGui

from functools import partial
import logging
import os
import re

from . import settingsWidget

logger = logging.getLogger(__name__)


# ------------------------------------------------- BASE INPUT WIDGETS -------------------------------------------------
class InputWidget(QtWidgets.QWidget):
    """Base class for custom input widgets. Custom input widgets are widgets that are used to edit a parameter in a
    custom UI. They should be used in conjunction with the ProceduralSettingsInput class.
    """

    def __init__(self, parent=None):
        super().__init__(parent)

        self.settingsLabel = QtWidgets.QLabel()
        self.settingsLabel.setFixedWidth(100)
        self.settingsLabel.setWordWrap(True)
        self.settingsLabel.setAlignment(QtCore.Qt.AlignRight | QtCore.Qt.AlignVCenter)

        self.inputWidget = QtWidgets.QWidget()
        self.inputLayout = QtWidgets.QHBoxLayout()
        self.inputWidget.setFixedWidth(250)
        self.inputLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.inputLayout.setContentsMargins(0, 0, 0, 0)
        self.inputWidget.setLayout(self.inputLayout)

    def setTitle(self, title):
        self.settingsLabel.setText(title)
        self.settingsLabel.setToolTip(title)

    @staticmethod
    def convertDisplayName(name: str):
        """Convert the variable name to a display name."""
        name = re.sub(r'(?<=[a-z])(?=[A-Z])', ' ', name)
        name = name.title()
        return name


class SmallInputWidget(InputWidget):
    """A widget that contains a label and a small input widget"""

    def __init__(self, parent=None):
        super().__init__(parent)

        self.layout = QtWidgets.QHBoxLayout()
        self.setLayout(self.layout)

        self.layout.addWidget(self.settingsLabel)
        self.layout.addWidget(self.inputWidget)


class LargeInputWidget(InputWidget):
    """A widget that contains a group box that displays the title and the input widget"""

    def __init__(self, parent=None, isVertical=False):
        super().__init__(parent)

        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)

        self.inputWidget = QtWidgets.QGroupBox(self)
        if isVertical:
            self.inputLayout = QtWidgets.QVBoxLayout()
        else:
            self.inputLayout = QtWidgets.QHBoxLayout()
        self.inputLayout.setAlignment(QtCore.Qt.AlignLeft | QtCore.Qt.AlignVCenter)
        self.inputLayout.setContentsMargins(0, 0, 0, 0)
        self.inputWidget.setLayout(self.inputLayout)
        self.layout.addWidget(self.inputWidget)

        # Set size policy to expand horizontally
        self.inputWidget.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.settingsLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)

    def setTitle(self, title):
        self.inputWidget.setTitle(str(title))


# -------------------------------------------------- UTILITY FUNCTIONS -------------------------------------------------
def createResetToDefaultButton(parent=None) -> QtWidgets.QPushButton:
    """Return a button that resets the value to the default value."""
    resetToDefaultButton = QtWidgets.QPushButton(parent)
    # resetToDefaultButton.setIcon(QtGui.QIcon(os.path.join(getIconPath(), "reload.png")))
    # TODO: Icon
    resetToDefaultButton.setMaximumHeight(15)
    resetToDefaultButton.setMaximumWidth(15)
    resetToDefaultButton.setToolTip("Reset to default")

    return resetToDefaultButton


def createAddRemoveButtons(bulkAdd=False, addSelected=False):
    """Creates a set of buttons for adding and removing items from a list or dict.
    Also has a flag for creating a button for adding multiple items at once."""
    buttonFrame = QtWidgets.QGroupBox()
    buttonFrame.setMinimumHeight(25)
    buttonFrame.setMaximumHeight(25)

    buttonFrameLayout = QtWidgets.QHBoxLayout()
    buttonFrameLayout.setContentsMargins(0, 0, 0, 0)
    buttonFrameLayout.setSpacing(0)
    buttonFrame.setLayout(buttonFrameLayout)
    buttonFrameLayout.setAlignment(QtCore.Qt.AlignLeft)

    addItemButton = QtWidgets.QPushButton()
    addItemButton.setText("+")
    addItemButton.setMinimumWidth(25)
    addItemButton.setMaximumWidth(25)
    addItemButton.setMinimumHeight(25)
    addItemButton.setMaximumHeight(25)
    addItemButton.resize(25, 25)
    addItemButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    addItemButton.setToolTip("Add Item")
    buttonFrame.layout().addWidget(addItemButton)

    removeItemButton = QtWidgets.QPushButton()
    removeItemButton.setText("-")
    removeItemButton.resize(25, 25)
    removeItemButton.setMinimumWidth(25)
    removeItemButton.setMaximumWidth(25)
    removeItemButton.setMinimumHeight(25)
    removeItemButton.setMaximumHeight(25)
    removeItemButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
    removeItemButton.setToolTip("Remove Item")
    buttonFrame.layout().addWidget(removeItemButton)

    if bulkAdd:
        bulkAddButton = QtWidgets.QPushButton()
        bulkAddButton.setText("++")
        bulkAddButton.resize(25, 25)
        bulkAddButton.setMinimumWidth(25)
        bulkAddButton.setMaximumWidth(25)
        bulkAddButton.setMinimumHeight(25)
        bulkAddButton.setMaximumHeight(25)
        bulkAddButton.setSizePolicy(QtWidgets.QSizePolicy.Fixed, QtWidgets.QSizePolicy.Fixed)
        bulkAddButton.setToolTip("Bulk Add Items")
        buttonFrame.layout().addWidget(bulkAddButton)

    if addSelected:
        addSelectedButton = QtWidgets.QPushButton()
        addSelectedButton.setText("Add Selected")
        addSelectedButton.setMinimumHeight(25)
        addSelectedButton.setMaximumHeight(25)
        addSelectedButton.setToolTip("Add selected items from the scene")
        buttonFrame.layout().addWidget(addSelectedButton)

    if bulkAdd and addSelected:
        return buttonFrame, addItemButton, removeItemButton, bulkAddButton, addSelectedButton

    elif bulkAdd:
        return buttonFrame, addItemButton, removeItemButton, bulkAddButton

    elif addSelected:
        return buttonFrame, addItemButton, removeItemButton, addSelectedButton

    return buttonFrame, addItemButton, removeItemButton


# ------------------------------------------------- INPUT WIDGETS ------------------------------------------------------
class TextInputWidget(SmallInputWidget):
    """A widget that lets the user edit a variable in a line edit."""

    def __init__(self, inObject, var, parent=None):
        """Initialize the widget."""
        super().__init__(parent)

        self.inObject = inObject
        self.var = var

        if isinstance(var, str):
            self.val = getattr(self.inObject, self.var)
            self.name = var
            self.displayName = self.convertDisplayName(var)
            self.defaultValue = None

            self.setupUI()
            return

        self.val = getattr(self.inObject, self.var.name)
        self.name = self.var.name
        self.displayName = self.var.displayName
        self.defaultValue = self.var.defaultValue

        self.setupUI()

    def setupUI(self):
        """Set up the UI."""
        self.setTitle(self.displayName)

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setText(str(self.val))
        self.lineEdit.textEdited.connect(partial(self._updateInObject, False))
        self.lineEdit.editingFinished.connect(partial(self._updateInObject, True))
        self.inputLayout.addWidget(self.lineEdit)

        if self.defaultValue is not None:
            resetToDefaultButton = createResetToDefaultButton()
            self.inputLayout.addWidget(resetToDefaultButton)

            def changeLineEditTextColor(lineEdit, defaultValue, *args):
                if lineEdit.text() == str(defaultValue):
                    lineEdit.setStyleSheet("color: #ffffff")
                    resetToDefaultButton.setHidden(True)
                else:
                    lineEdit.setStyleSheet("color: #dad8a7")
                    resetToDefaultButton.setHidden(False)

            def resetToDefault():
                self.lineEdit.setText(str(self.defaultValue))
                self._updateInObject()
                changeLineEditTextColor(self.lineEdit, self.defaultValue)

            resetToDefaultButton.clicked.connect(resetToDefault)

            changeLineEditTextColor(self.lineEdit, self.defaultValue)
            self.lineEdit.textEdited.connect(partial(changeLineEditTextColor, self.lineEdit, self.defaultValue))

    def _updateInObject(self, stripWhitespace=False, *args):
        """Update the inObject when the text is edited."""
        if getattr(self.inObject, self.name) is None:
            logger.error(f"The variable {self.name} is not set in {self.inObject}.")
            return

        newValue = self.lineEdit.text()

        if stripWhitespace:
            # Strip any whitespace from the end of the string
            newValue = newValue.rstrip()
            # Set the text to the new value in case it was changed (e.g. by stripping whitespace)
            self.lineEdit.setText(newValue)

        setattr(self.inObject, self.name, newValue)


class ComboBoxInputWidget(SmallInputWidget):
    """A widget that lets the user edit a variable in a combo box."""

    def __init__(self, parent=None, inObject=None, var=None):
        """A widget that lets the user edit a variable in a combo box"""
        super().__init__(parent)

        self.inObject = inObject
        self.var = var

        if isinstance(self.var, str):
            self.val = getattr(self.inObject, self.var)
            self.name = self.var
            self.displayName = self.convertDisplayName(self.var)
            self.defaultValue = None
            self.items = []

            self.setupUI()
            return

        self.val = getattr(self.inObject, self.var.name)
        self.name = self.var.name
        self.displayName = self.var.displayName
        self.defaultValue = self.var.defaultValue
        self.items = self.var.comboBoxItems

        self.setupUI()

    def setupUI(self):
        """Sets up the UI"""
        self.setTitle(self.displayName)

        self.combo = QtWidgets.QComboBox()
        self.combo.addItems(self.items)
        self.combo.setCurrentText(str(self.val))
        self.combo.currentTextChanged.connect(self._updateInObject)
        self.inputLayout.addWidget(self.combo)

    def _updateInObject(self):
        """Updates the inObject with the current value of the combo box"""
        setattr(self.inObject, self.name, self.combo.currentText())


class BoolInputWidget(SmallInputWidget):
    """A widget that lets the user edit a boolean variable with a check box."""

    def __init__(self, inObject, var, parent=None):
        """Initialize the widget."""
        super().__init__(parent)

        self.inObject = inObject
        self.var = var

        if isinstance(var, str):
            self.val = getattr(self.inObject, self.var)
            self.name = var
            self.displayName = self.convertDisplayName(var)
            self.defaultValue = None

            self.setupUI()
            return

        self.val = getattr(self.inObject, self.var.name)
        self.name = self.var.name
        self.displayName = self.var.displayName
        self.defaultValue = self.var.defaultValue

        self.setupUI()

    def setupUI(self):
        """Set up the UI."""
        self.setTitle(self.displayName)

        self.checkBox = QtWidgets.QCheckBox()
        self.checkBox.setChecked(self.val)
        self.checkBox.stateChanged.connect(self._updateInObject)
        self.inputLayout.addWidget(self.checkBox)

        if self.defaultValue is not None:
            resetToDefaultButton = createResetToDefaultButton()
            self.inputLayout.addWidget(resetToDefaultButton)

            def resetToDefault():
                self.checkBox.setChecked(self.defaultValue)
                self._updateInObject()

            resetToDefaultButton.clicked.connect(resetToDefault)

    def _updateInObject(self, *args):
        """Update the inObject when the check box is checked or unchecked."""
        if getattr(self.inObject, self.name) is None:
            logger.error(f"The variable {self.name} is not set in {self.inObject}.")
            return

        newValue = self.checkBox.isChecked()
        setattr(self.inObject, self.name, newValue)


class NumberInputWidget(SmallInputWidget):
    """A widget that lets the user edit a number variable with a line edit and slider."""

    def __init__(self, inObject, var, parent=None):
        super().__init__(parent)

        self.inObject = inObject
        self.var = var

        if isinstance(var, str):
            self.val = getattr(self.inObject, self.var)
            self.isFloat = "." in str(self.val)
            if self.isFloat:
                self.decimalPlaces = len(str(self.val).split(".")[1])
            else:
                self.decimalPlaces = 0
            self.name = var
            self.displayName = self.convertDisplayName(var)
            self.defaultValue = None

            self.setupUI()
            return

        self.val = getattr(self.inObject, self.var.name)
        self.isFloat = "." in str(self.val)
        if self.isFloat:
            self.decimalPlaces = len(str(self.val).split(".")[1])
        else:
            self.decimalPlaces = 0
        self.name = self.var.name
        self.displayName = self.var.displayName
        self.defaultValue = self.var.defaultValue

        self.setupUI()

    def setupUI(self):
        """Set up the UI."""
        self.setTitle(self.displayName)

        self.lineEdit = QtWidgets.QLineEdit()
        self.lineEdit.setText(str(self.val))
        self.lineEdit.textEdited.connect(self._text_changed)
        # self.lineEdit.editingFinished.connect(partial(self._updateInObject, True))
        self.lineEdit.setValidator(QtGui.QDoubleValidator())
        self.inputLayout.addWidget(self.lineEdit)

        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.setRange(0, 100)
        self.slider.setValue(self.val)
        self.slider.sliderMoved.connect(self._slider_changed)
        self.inputLayout.addWidget(self.slider)

        if self.defaultValue is not None:
            resetToDefaultButton = createResetToDefaultButton()
            self.inputLayout.addWidget(resetToDefaultButton)

            def resetToDefault():
                self.slider.setValue(self.defaultValue)
                self._updateInObject()

            resetToDefaultButton.clicked.connect(resetToDefault)

    def _updateInObject(self, *args):
        """Update the inObject when the text is edited."""
        if getattr(self.inObject, self.name) is None:
            logger.error(f"The variable {self.name} is not set in {self.inObject}.")
            return

        setattr(self.inObject, self.name, self.val)

    def _text_changed(self, text):
        """Update the slider when the text is changed."""
        if text == "":
            return

        self.isFloat = "." in text

        if self.isFloat:
            self.val = float(text)

            if self.val > self.slider.maximum():
                self.slider.setMaximum(self.val)

            self.decimalPlaces = len(text.split(".")[1])
            if self.decimalPlaces > 5:
                self.decimalPlaces = 5
            scaledValue = int(float(text) * (10 ** self.decimalPlaces))
            self.slider.setValue(scaledValue)

        else:
            self.val = int(text)

            if self.val > self.slider.maximum():
                self.slider.setMaximum(self.val)

            self.slider.setValue(self.val)

        if self.defaultValue is not None:
            self.changeNumberInputTextColor()
        self._updateInObject()

    def _slider_changed(self, value):
        """Update the line edit when the slider is moved."""
        if self.isFloat:
            self.val = value / self.decimalPlaces
            self.lineEdit.setText(str(self.val))
        else:
            self.val = value
            self.lineEdit.setText(str(self.val))

        if self.defaultValue is not None:
            self.changeNumberInputTextColor()
        self._updateInObject()


class FileInputWidget(LargeInputWidget):
    """A widget that lets the user set a file variable."""

    def __init__(self, parent=None, inObject=None, var=None):
        """Initialize the widget.

        Arguments:
            parent: The parent widget
            inObject: The object that contains the variable
            var: The variable to set (must be a uiParam object)
        """
        super().__init__(parent)

        self.inObject = inObject
        self.var = var

        self.displayName = self.var.displayName
        self.fileMode = "dir" if var.isDir else "file"
        self.startDirectory = var.startDirectory
        self.setupStartDir()

        self.setupUI()

    def setupUI(self):
        """Set up the UI."""
        self.setTitle(self.displayName)

        midWidget = QtWidgets.QWidget()
        midLayout = QtWidgets.QHBoxLayout()
        midWidget.setLayout(midLayout)

        val = getattr(self.inObject, self.var.name)
        val = os.path.normpath(val)
        self.valLabel = QtWidgets.QLabel(val)
        self.valLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.valLabel.setToolTip(val)
        midLayout.addWidget(self.valLabel)
        self.abbreviateValLabel()

        button = QtWidgets.QPushButton()
        button.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "folder.png")))
        # TODO: Icon
        button.setToolTip("Browse")
        button.setFixedWidth(26)
        button.clicked.connect(self.setVal)
        midLayout.addWidget(button)

        self.inputLayout.addWidget(midWidget)

    def setupStartDir(self):
        """Set up the start directory for the file dialog."""
        self.startDirectory = self.var.startDirectory

        if self.startDirectory == "" or self.startDirectory == "." or self.startDirectory is None or \
                not os.path.exists(self.startDirectory) or not os.path.isdir(self.startDirectory):
            self.startDirectory = os.path.expanduser("~")

    def abbreviateValLabel(self):
        """Abbreviate the file path if it's too long."""
        # TODO: Also call this on resize
        fileNameWidth = self.valLabel.fontMetrics().boundingRect(self.valLabel.text()).width()
        widthTolerance = 500
        i = 5
        while fileNameWidth > widthTolerance and i > 0:
            splitFileName = os.path.normpath(self.valLabel.text()).split(os.sep)
            beginning = os.sep.join(splitFileName[0:2])
            end = os.sep.join(splitFileName[-i:])
            abbreviatedFileName = f"{beginning}...{end}"
            self.valLabel.setText(abbreviatedFileName)

            fileNameWidth = self.valLabel.fontMetrics().boundingRect(self.valLabel.text()).width()
            i -= 1

    def setVal(self):
        """Set the value of the variable."""
        dialog = QtWidgets.QFileDialog()
        dialog.setDirectory(self.startDirectory)

        if self.fileMode == "file":
            dialog.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        elif self.fileMode == "dir":
            dialog.setFileMode(QtWidgets.QFileDialog.Directory)

        if not dialog.exec_():
            return

        selectedFile = os.path.normpath(dialog.selectedFiles()[0])

        setattr(self.inObject, self.var.name, selectedFile)

        # Update UI
        self.valLabel.setText(selectedFile)
        self.valLabel.setToolTip(selectedFile)
        self.abbreviateValLabel()


class FunctionInputWidget(LargeInputWidget):
    """A widget that lets the user run a function and edit the function's arguments."""

    def __init__(self, parent=None, inObject=None, var=None):
        """Initialize the widget."""
        super().__init__(parent, isVertical=True)

        self.inObject = inObject
        self.var = var

        if isinstance(self.var, str):
            self.displayName = self.convertDisplayName(self.var)
            self.function = getattr(self.inObject, self.var)
            self.args = []
            self.setupUI()
            return

        self.displayName = self.var.displayName
        self.function = getattr(self.inObject, self.var.name)
        self.args = self.var.args

        self.setupUI()

    def setupUI(self):
        """Set up the UI."""
        self.setTitle(self.displayName)

        if self.args != []:
            # Add another settings widget for the function args
            print(f"adding args {self.args}")
            self.funcSettingsWidget = settingsWidget.SettingsWidget(inObject=self.inObject, variables=self.args)
            self.inputLayout.addWidget(self.funcSettingsWidget)

        self.runLayout = QtWidgets.QHBoxLayout()
        self.runLayout.setAlignment(QtCore.Qt.AlignLeft)
        self.runLayout.setSpacing(0)
        self.inputLayout.addLayout(self.runLayout)

        self.spacer = QtWidgets.QWidget()
        self.spacer.setFixedWidth(50)
        self.runLayout.addWidget(self.spacer)

        self.runButton = QtWidgets.QPushButton("Run")
        self.runButton.setFixedWidth(75)
        self.runButton.clicked.connect(self.function)
        # TODO: Currently, the function is run but the arguments are not actually passed to it - the "arguments" are
        # actually other variables in the inObject. Should figure out whether we should keep this functionality or
        # not.
        self.runLayout.addWidget(self.runButton)

        self.bottomSpacer = QtWidgets.QWidget()
        self.bottomSpacer.setFixedHeight(10)
        self.inputLayout.addWidget(self.bottomSpacer)


class ListInputWidget(LargeInputWidget):
    """Subclass of LargeCustomInputWidget that allows the user to edit a list of values."""

    def __init__(self, parent=None, inObject=None, var=None):
        """
        A widget that allows the user to edit a list of values.

        Arguments:
            parent: The parent widget.
            inObject: The object that contains the list to be edited.
            var: The name of the list to be edited, or a Variable object.
        """

        super().__init__(parent)
        self.inObject = inObject
        self.var = var

        if isinstance(self.var, str):
            self.listMode = "default"
            self.name = self.convertDisplayName(self.var)
            self.varName = self.var
            self.inList = vars(self.inObject)[self.var]
            self.defaultValue = None
            self.isMultiVar = False
            self.setupUI()
            return

        self.name = self.var.displayName
        self.varName = self.var.name
        self.inList = vars(self.inObject)[self.var.name]
        self.defaultValue = self.var.defaultValue
        self.isMultiVar = self.var.isMultiVar

        self.listMode = "default"
        if self.var.isVariableSize:
            self.listMode = "variable"
        elif 1 < len(self.inList) < 5 and all(isinstance(item, (int, float)) for item in self.inList):
            self.listMode = "vector"

        self.setupUI()

    def setupUI(self):
        self.setTitle(self.name)
        self.layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.layout)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        if self.listMode == "variable":
            self._setupUIVariableSize()

        elif self.listMode == "vector":
            self._setupUIVectorStyle()

        else:
            self._setupUIDefault()

    def addItem(self):
        """Adds an item to the list"""
        itemName = "Item"
        # Check for duplicate names and append a number if necessary
        if itemName in self.inList:
            i = 1
            while itemName + str(i) in self.inList:
                i += 1
            itemName += str(i)

        self.inList.append(itemName)
        self._updateUIVariableSize()

    def removeItems(self):
        """Removes any selected item(s) from the list"""
        # Get selected indexes
        selectedIndexes = self.listInputWidget.selectedIndexes()
        if not selectedIndexes:
            return

        selectedIndexes.reverse()
        for index in selectedIndexes:
            self.inList.pop(index.row())

        self._updateUIVariableSize()

    def _setupUIVariableSize(self):
        """Sets up a variable size list widget"""
        topWidget = QtWidgets.QWidget()
        topLayout = QtWidgets.QVBoxLayout()
        topWidget.setLayout(topLayout)

        # Add/Remove buttons
        buttonFrame, addItemButton, removeItemButton = createAddRemoveButtons()

        # List widget
        self.listInputWidget = QtWidgets.QListWidget()
        self.listInputWidget.setAlternatingRowColors(True)
        listLayout = QtWidgets.QHBoxLayout()
        self.listInputWidget.setLayout(listLayout)
        self.listInputWidget.setSpacing(0)
        self.listInputWidget.setContentsMargins(0, 0, 0, 0)
        self.listInputWidget.itemChanged.connect(self._updateInObjectVariableSize)
        self.listInputWidget.setSelectionMode(QtWidgets.QAbstractItemView.ExtendedSelection)

        # Add items to list
        for i, item in enumerate(self.inList):
            self.listInputWidget.addItem(item)
            flags = QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            self.listInputWidget.item(i).setFlags(flags)
            self.listInputWidget.item(i).setSizeHint(QtCore.QSize(200, 25))

        # Connections
        addItemButton.clicked.connect(self.addItem)
        removeItemButton.clicked.connect(self.removeItems)

        topLayout.addWidget(buttonFrame)
        topLayout.addWidget(self.listInputWidget)
        self.inputLayout.addWidget(topWidget)

    def _setupUIVectorStyle(self):
        """Sets up a vector style list widget"""

        gridWidget = QtWidgets.QWidget()
        gridLayout = QtWidgets.QGridLayout(gridWidget)
        gridWidget.setLayout(gridLayout)
        gridLayout.setContentsMargins(0, 0, 0, 0)
        gridLayout.setSpacing(0)
        gridLayout.setAlignment(QtCore.Qt.AlignLeft)

        spacerWidget = QtWidgets.QWidget()
        spacerWidget.setMaximumWidth(10)
        gridLayout.addWidget(spacerWidget, 0, 0)

        if self.defaultValue is not None:
            resetToDefaultButton = createResetToDefaultButton(parent=self)

            def changeListWidgetColor(lineEdit, defaultValue, *args):
                if lineEdit.text() == str(defaultValue):
                    lineEdit.setStyleSheet("color: #FFFFFF")
                    resetToDefaultButton.setHidden(True)
                else:
                    lineEdit.setStyleSheet("color: #dad8a7")
                    resetToDefaultButton.setHidden(False)

            def resetToDefault():
                for i in range(len(self.inList)):
                    self.inList[i] = self.defaultValue[i]
                    lineEdit = gridLayout.itemAtPosition(0, i).widget()
                    if not isinstance(lineEdit, QtWidgets.QLineEdit):
                        continue
                    lineEdit.setText(str(self.defaultValue[i]))
                    changeListWidgetColor(lineEdit, self.defaultValue[i])

                self._updateInObject(self.varName, self.defaultValue)

            resetToDefaultButton.clicked.connect(resetToDefault)

        for i in range(len(self.inList)):
            lineEdit = QtWidgets.QLineEdit()
            lineEdit.setText(str(self.inList[i]))
            lineEdit.setMaximumWidth(100)
            if self.isMultiVar:
                lineEdit.textEdited.connect(partial(self._updateInObject, self.var.inVars[i]))
            else:
                lineEdit.textEdited.connect(partial(self._updateInObjectList, self.varName, i))
                pass

            if self.defaultValue is not None:
                changeListWidgetColor(lineEdit, self.defaultValue[i])
                lineEdit.textEdited.connect(partial(changeListWidgetColor, lineEdit, self.defaultValue[i]))

            gridLayout.addWidget(lineEdit, 0, i + 1)

        self.inputLayout.addWidget(gridWidget)
        if self.defaultValue is not None:
            gridLayout.addWidget(resetToDefaultButton, 0, len(self.inList) + 1)
            resetToDefaultButton.setHidden(self.inList == self.defaultValue)

    def _setupUIDefault(self):
        """Sets up a default list widget"""
        topWidget = QtWidgets.QWidget()
        # topWidget.setStyleSheet("background-color: #FF0000;")
        topLayout = QtWidgets.QVBoxLayout()
        topLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        topWidget.setLayout(topLayout)

        if self.defaultValue is not None:
            resetToDefaultButton = createResetToDefaultButton()

            def resetToDefault():
                for i in range(len(self.inList)):
                    self.inList[i] = self.defaultValue[i]
                    lineEdit = topLayout.itemAt(i).widget().layout().itemAt(0).widget()
                    if not isinstance(lineEdit, QtWidgets.QLineEdit):
                        continue
                    lineEdit.setText(str(self.defaultValue[i]))
                    changeLineEditColor(lineEdit, self.defaultValue[i])

                self._updateInObject(self.varName, self.defaultValue)

            resetToDefaultButton.clicked.connect(resetToDefault)

            def changeLineEditColor(lineEdit, defaultValue, *args):
                if lineEdit.text() == str(defaultValue):
                    lineEdit.setStyleSheet("color: #FFFFFF")
                    resetToDefaultButton.setHidden(True)
                else:
                    lineEdit.setStyleSheet("color: #dad8a7")
                    resetToDefaultButton.setHidden(False)

        for i, item in enumerate(self.inList):
            lineWidget = QtWidgets.QWidget()
            hBox = QtWidgets.QHBoxLayout()
            lineWidget.setLayout(hBox)

            lineEdit = QtWidgets.QLineEdit(str(item))
            lineEdit.setFixedWidth(200)
            if self.isMultiVar:
                lineEdit.textEdited.connect(partial(self._updateInObject, self.var.inVars[i]))
            else:
                lineEdit.textEdited.connect(partial(self._updateInObjectList, self.varName, i))

            if self.defaultValue is not None:
                changeLineEditColor(lineEdit, self.defaultValue[i])
                lineEdit.textEdited.connect(partial(changeLineEditColor, lineEdit, self.defaultValue[i]))

            hBox.addWidget(lineEdit)

            topLayout.addWidget(lineWidget)

        if self.defaultValue is not None:

            topLayout.addWidget(resetToDefaultButton)
            resetToDefaultButton.setHidden(self.inList == self.defaultValue)

        self.inputLayout.setAlignment(QtCore.Qt.AlignTop | QtCore.Qt.AlignLeft)
        self.inputLayout.addWidget(topWidget)

    def _updateUIVariableSize(self):
        """Updates the UI to match the size of the variable"""
        # Clear list
        self.listInputWidget.clear()

        # Add items to list
        for i, item in enumerate(self.inList):
            self.listInputWidget.addItem(item)
            flags = QtCore.Qt.ItemIsEditable | QtCore.Qt.ItemIsEnabled | QtCore.Qt.ItemIsSelectable
            self.listInputWidget.item(i).setFlags(flags)
            self.listInputWidget.item(i).setSizeHint(QtCore.QSize(200, 25))

    def _updateInObject(self, var, newValue, *args):
        """Updates self.inObject with the provided var and value"""
        if getattr(self.inObject, var) is None:
            logger.error(f"The variable {var} is not set on the object {self.inObject}")
            return

        setattr(self.inObject, var, newValue)

    def _updateInObjectList(self, var, index, newValue, *args):
        """Update self.inObject with the provided var and value at the given index."""
        if getattr(self.inObject, var) is None:
            logger.error(f"The variable {var} is not set on the object {self.inObject}")
            return

        if isinstance(getattr(self.inObject, var)[index], int):
            try:
                newValue = int(newValue)
            except Exception:
                newValue = str(newValue)
        elif isinstance(getattr(self.inObject, var)[index], float):
            try:
                newValue = float(newValue)
            except Exception:
                newValue = str(newValue)

        getattr(self.inObject, var)[index] = newValue

    def _updateInObjectVariableSize(self, listItem):
        """Special wrapper function from the variable size list widget"""
        row = self.listInputWidget.row(listItem)

        if self.var.isMultiVar:
            self._updateInObject(self.var.inVars[row], listItem.text())
        else:
            self._updateInObjectList(self.varName, row, listItem.text())
