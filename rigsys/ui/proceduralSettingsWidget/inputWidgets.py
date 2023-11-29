"""Input widgets for procedural settings widget."""

from PySide2 import QtWidgets, QtCore, QtGui

from functools import partial
import logging
import os
import re

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
    # TODO: Convert

    def __init__(self, parent=None, inObject=None, var=None):
        """Initialize the widget.

        Arguments:
            parent: The parent widget
            inObject: The object that contains the variable
            var: The variable to set (must be a uiParam object)
        """
        super().__init__(parent)

        self.inObject = inObject
        self.var: uiParams._strUIParameter = var

        self.fileMode = "dir" if var.isDir else "file"
        self.startDirectory = var.startDirectory
        self.setupStartDir()

        self.setupUI()

    def setupUI(self):
        """Set up the UI."""
        self.setTitle(self.var.displayName)

        midWidget = QtWidgets.QWidget()
        midLayout = QtWidgets.QHBoxLayout()
        midWidget.setLayout(midLayout)

        val = getattr(self.inObject, self.var.name)
        val = os.path.normpath(val)
        val = stringUtilities.compressRelativePath(val)
        self.valLabel = QtWidgets.QLabel(val)
        self.valLabel.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        self.valLabel.setToolTip(val)
        midLayout.addWidget(self.valLabel)
        self.abbreviateValLabel()

        button = QtWidgets.QPushButton()
        button.setIcon(QtGui.QIcon(os.path.join(os.path.dirname(__file__), "images", "folder.png")))
        button.setToolTip("Browse")
        button.setFixedWidth(26)
        button.clicked.connect(self.setVal)
        midLayout.addWidget(button)

        self.inputLayout.addWidget(midWidget)

    def setupStartDir(self):
        """Set up the start directory for the file dialog."""
        self.startDirectory = self.var.startDirectory

        if self.startDirectory == "character":
            import zubio.api.api_character as api_character
            self.startDirectory = api_character.getCharacter()
            self.startDirectory = api_character.getCharacterFolderPath(self.startDirectory)

        elif self.startDirectory == "production":
            if api_production.checkProduction():
                self.startDirectory = api_production.getProduction()
            else:
                self.startDirectory = os.path.expanduser("~")

        elif self.startDirectory == "" or self.startDirectory == "." or self.startDirectory is None or \
                not os.path.exists(self.startDirectory) or not os.path.isdir(self.startDirectory):
            if api_production.checkProduction():
                self.startDirectory = api_production.getProduction()
            else:
                self.startDirectory = os.path.expanduser("~")

    def abbreviateValLabel(self):
        """Abbreviate the file path if it's too long."""
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
        selectedFile = stringUtilities.compressRelativePath(selectedFile)

        setattr(self.inObject, self.var.name, selectedFile)

        # Update UI
        self.valLabel.setText(selectedFile)
        self.valLabel.setToolTip(selectedFile)
        self.abbreviateValLabel()

        # Set mirrored
        if not hasattr(self.inObject, "_mirroredObject") or not hasattr(self.inObject, "isMirror"):
            return

        if self.inObject._mirroredObject is None or not self.inObject.isMirror or \
                not self.inObject._mirroredObject.isMirrored:
            return

        try:
            mirroredString = stringUtilities.mirrorString(selectedFile)
            setattr(self.inObject._mirroredObject, self.var.name, mirroredString)
        except AttributeError:
            print(f"Mirrored object has no attribute {self.var.name}")
