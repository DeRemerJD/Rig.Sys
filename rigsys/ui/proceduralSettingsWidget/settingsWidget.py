"""Widget to display and edit procedural settings."""

import logging

from PySide2 import QtWidgets, QtCore, QtGui

from . import parameters
from . import inputWidgets

logger = logging.getLogger(__name__)


class SettingsWidget(QtWidgets.QWidget):
    """Widget to display and edit procedural settings."""

    def __init__(self, inObject, variables: list = None, parent=None):
        """Initialize the widget.

        Arguments:
            inObject {object} -- The object to display and edit.
            variables {list} -- The variables to display and edit. This can be a list of strings, or a list of tuples
                with the first element being the variable name and the second element being the label text. Defaults
                to None.
        """
        super().__init__(parent=parent)

        self.inObject = inObject
        self.variables = variables
        if self.variables is None:
            self.variables = vars(self.inObject).keys()

        self.setupVariables()

    def setupVariables(self):
        """Set up the variables."""
        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        for variable in self.variables:
            self.addVariable(variable)

    def addVariable(self, variable_name):
        """Add a variable to the widget."""
        value = getattr(self.inObject, variable_name)

        if isinstance(value, bool):
            bool_input_widget = inputWidgets.BoolInputWidget(
                inObject=self.inObject,
                var=variable_name,
                parent=self
            )
            self.layout.addWidget(bool_input_widget)

        elif isinstance(value, str):
            str_input_widget = inputWidgets.TextInputWidget(
                inObject=self.inObject,
                var=variable_name,
                parent=self
            )
            self.layout.addWidget(str_input_widget)

        elif isinstance(value, int) or isinstance(value, float):
            number_input_widget = inputWidgets.NumberInputWidget(
                inObject=self.inObject,
                var=variable_name,
                parent=self
            )
            self.layout.addWidget(number_input_widget)

        else:
            logger.error(f"Unsupported variable type {type(value)} for variable {variable_name}")
