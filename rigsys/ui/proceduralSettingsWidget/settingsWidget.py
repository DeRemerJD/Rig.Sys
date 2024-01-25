"""Widget to display and edit procedural settings."""

# TESTING CODE ONLY - REMOVE BEFORE MERGING
import os
from pprint import pprint
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir)))
# TESTING CODE ONLY - REMOVE BEFORE MERGING

import inspect
import logging

from PySide2 import QtWidgets, QtCore

from proceduralSettingsWidget import parameters
from proceduralSettingsWidget import inputWidgets

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

        testParam = parameters._boolUIParam("testParam")
        testParam2 = parameters.uiParam(self.inObject, "testFile", isFile=True)
        # Hitting problems because we have a pip-installed version of proceduralSettingsWidget and a local version
        # Probably want to remove the pip-installed version

        self.setupVariables()

    def setupVariables(self):
        """Set up the variables."""
        self.main_layout = QtWidgets.QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.main_layout)

        for variable in self.variables:
            self.add_variable(variable)

    def add_variable(self, variable):
        """Add a variable to the widget."""
        if isinstance(variable, str):
            self.add_variable_simple(variable)
        elif isinstance(variable, parameters._baseUIParam):
            self.add_variable_uiParam(variable)
        else:
            logger.error(f"Unsupported variable type {type(variable)} for variable {variable}. "
                         f"Expected str or {(parameters._baseUIParam)}")

    def add_variable_simple(self, variable):
        """Add a string variable to the widget."""
        value = getattr(self.inObject, variable)

        if isinstance(value, bool):
            bool_input_widget = inputWidgets.BoolInputWidget(
                inObject=self.inObject,
                var=variable,
                parent=self
            )
            self.main_layout.addWidget(bool_input_widget)

        elif isinstance(value, str):
            str_input_widget = inputWidgets.TextInputWidget(
                inObject=self.inObject,
                var=variable,
                parent=self
            )
            self.main_layout.addWidget(str_input_widget)

        elif isinstance(value, int) or isinstance(value, float):
            number_input_widget = inputWidgets.NumberInputWidget(
                inObject=self.inObject,
                var=variable,
                parent=self
            )
            self.main_layout.addWidget(number_input_widget)

        elif isinstance(value, list):
            # TODO
            pass

        elif isinstance(value, dict):
            # TODO
            pass

        elif isinstance(value, tuple):
            # TODO
            pass

        elif inspect.ismethod(value):
            function_input_widget = inputWidgets.FunctionInputWidget(
                inObject=self.inObject,
                var=variable,
                parent=self
            )
            self.main_layout.addWidget(function_input_widget)

        else:
            logger.error(f"Unsupported variable type {type(value)} for variable {variable}")

    def add_variable_uiParam(self, variable: parameters._baseUIParam):
        """Add a uiParam variable to the widget."""
        if isinstance(variable, parameters._boolUIParam):
            bool_input_widget = inputWidgets.BoolInputWidget(
                inObject=self.inObject,
                var=variable.name,
                parent=self
            )
            self.main_layout.addWidget(bool_input_widget)

        elif isinstance(variable, parameters._strUIParameter) and (variable.isFile or variable.isDir):
            file_input_widget = inputWidgets.FileInputWidget(
                inObject=self.inObject,
                var=variable,
                parent=self
            )
            self.main_layout.addWidget(file_input_widget)

        elif isinstance(variable, parameters._strUIParameter) and variable.isComboBox:
            combo_box_input_widget = inputWidgets.ComboBoxInputWidget(
                inObject=self.inObject,
                var=variable,
                parent=self
            )
            self.main_layout.addWidget(combo_box_input_widget)

        elif isinstance(variable, parameters._strUIParameter):
            str_input_widget = inputWidgets.TextInputWidget(
                inObject=self.inObject,
                var=variable,
                parent=self
            )
            self.main_layout.addWidget(str_input_widget)

        elif isinstance(variable, parameters._intUIParameter) or isinstance(variable, parameters._floatUIParameter):
            number_input_widget = inputWidgets.NumberInputWidget(
                inObject=self.inObject,
                var=variable,
                parent=self
            )
            self.main_layout.addWidget(number_input_widget)

        elif isinstance(variable, parameters._listUIParameter):
            # TODO
            pass

        elif isinstance(variable, parameters._dictUIParameter):
            # TODO
            pass

        elif isinstance(variable, parameters._tupleUIParameter):
            # TODO
            pass

        elif isinstance(variable, parameters._methodUIParameter):
            function_input_widget = inputWidgets.FunctionInputWidget(
                inObject=self.inObject,
                var=variable,
                parent=self
            )
            self.main_layout.addWidget(function_input_widget)

        else:
            logger.error(f"Unsupported variable type {type(variable)} for variable {variable}")


if __name__ == "__main__":
    app = QtWidgets.QApplication([])

    class TestObject:
        def __init__(self) -> None:
            self.int_variable = 1
            self.bool_variable = True
            self.str_variable = "test"
            self.file_variable = ""
            self.combo_box_var = "test_1"

            self.repetitions = 1

        def editables(self) -> list:
            return [
                parameters.uiParam(self, "int_variable"),
                parameters.uiParam(self, "bool_variable"),
                parameters.uiParam(self, "str_variable"),
                parameters.uiParam(self, "print_members", args=["repetitions"]),
                parameters.uiParam(self, "file_variable", isFile=True),
                parameters.uiParam(self, "combo_box_var", isComboBox=True,
                                   comboBoxItems=["test_1", "test_2", "test_3"]),
            ]

        def print_members(self):
            for _ in range(self.repetitions):
                print(f"int_variable: {self.int_variable}")
                print(f"bool_variable: {self.bool_variable}")
                print(f"str_variable: {self.str_variable}")

    mainWindow = QtWidgets.QMainWindow()
    mainWindow.setWindowTitle("Test Window")
    mainWindow.resize(400, 300)

    testObject = TestObject()

    widget = QtWidgets.QWidget()
    widget.main_layout = QtWidgets.QVBoxLayout()
    widget.setLayout(widget.main_layout)
    mainWindow.setCentralWidget(widget)

    settings_widget = SettingsWidget(inObject=testObject, variables=testObject.editables(), parent=mainWindow)
    widget.main_layout.addWidget(settings_widget)

    print_button = QtWidgets.QPushButton("Print Object Info")
    print_button.clicked.connect(lambda: pprint(vars(testObject)))
    widget.main_layout.addWidget(print_button)

    mainWindow.show()
    app.exec_()
