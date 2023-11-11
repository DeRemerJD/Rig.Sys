"""Input widgets for procedural settings widget."""

from PySide2 import QtWidgets, QtCore, QtGui

from functools import partial
import re


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
            cmds.error(f"The variable {self.name} is not set in {self.inObject}.")
            return

        newValue = self.lineEdit.text()

        if stripWhitespace:
            # Strip any whitespace from the end of the string
            newValue = newValue.rstrip()
            # Set the text to the new value in case it was changed (e.g. by stripping whitespace)
            self.lineEdit.setText(newValue)

        setattr(self.inObject, self.name, newValue)
