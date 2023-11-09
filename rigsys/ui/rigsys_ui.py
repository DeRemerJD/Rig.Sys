"""UI for rigsys."""


from PySide2 import QtWidgets, QtCore

from rigsys.ui.add_module_dialog import AddModuleDialog

import rigsys
import rigsys.modules as rigsys_modules


class RigUI(QtWidgets.QWidget):
    """A UI for rigsys."""

    def __init__(self):
        """Initialize the UI."""
        super().__init__()

        self.rig = rigsys.Rig()

        self.setup_ui()

    def setup_ui(self):
        """Set up the UI."""
        self.setWindowTitle("RigSys UI")
        self.resize(500, 500)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # General settings
        self.general_settings_widget = QtWidgets.QWidget()
        self.general_settings_layout = QtWidgets.QVBoxLayout()
        self.general_settings_widget.setLayout(self.general_settings_layout)
        # self.main_layout.addWidget(self.general_settings_widget)

        # Build order
        # TODO

        # Buttons setup
        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.buttons_widget.setLayout(self.buttons_layout)
        self.main_layout.addWidget(self.buttons_widget)

        # Add button
        self.add_button = QtWidgets.QPushButton("+")
        self.add_button.setFixedWidth(25)
        self.buttons_layout.addWidget(self.add_button)
        self.add_button.clicked.connect(self.add_module)

        # Remove button
        self.remove_button = QtWidgets.QPushButton("-")
        self.remove_button.setFixedWidth(25)
        self.buttons_layout.addWidget(self.remove_button)
        self.remove_button.clicked.connect(self.remove_module)

        self.module_splitter = QtWidgets.QSplitter()
        self.module_splitter.splitterMoved.connect(self.module_splitter.saveState)
        self.module_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.module_splitter.setOpaqueResize(False)
        self.main_layout.addWidget(self.module_splitter)
        # self.module_splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Module list
        self.module_list_widget = QtWidgets.QListWidget()
        self.module_list_widget.setAlternatingRowColors(True)
        self.module_splitter.addWidget(self.module_list_widget)

        # Module settings
        self.module_settings_widget = QtWidgets.QWidget()
        self.module_settings_layout = QtWidgets.QHBoxLayout()
        self.module_settings_layout.setAlignment(QtCore.Qt.AlignTop)
        self.module_settings_widget.setLayout(self.module_settings_layout)
        self.module_splitter.addWidget(self.module_settings_widget)

        self.module_settings_layout.addWidget(QtWidgets.QLabel("Module Settings"))

        # Build button
        self.build_button = QtWidgets.QPushButton("Build")
        self.build_button.setFixedHeight(50)
        self.build_button.clicked.connect(self.build_rig)
        self.main_layout.addWidget(self.build_button)

    def add_module(self):
        """Add a module to the rig."""
        dialog = AddModuleDialog()

        if dialog.exec_():
            selected_module_type = dialog.selected_module

            new_module_full_name = f"{dialog.get_selected_side()}_{dialog.selected_module}"
            new_module_full_name = self.check_duplicate_names(new_module_full_name)

            new_module = rigsys_modules.allModuleTypes[selected_module_type](self.rig)
            self.rig.motionModules[new_module_full_name] = new_module
            self.module_list_widget.addItem(new_module_full_name)

    def check_duplicate_names(self, name):
        """Ensure a name isn't a duplicate of an existing module."""
        if name not in self.rig.motionModules.keys():
            return name

        i = 0
        temp_name = name
        while temp_name in self.rig.motionModules.keys():
            i += 1
            temp_name = f"{name}_{i}"

        return temp_name

    def remove_module(self):
        """Remove a module from the rig."""
        print("Removing module")

    def build_rig(self):
        """Build the rig."""
        print("Building rig")
        self.rig.build()  # TODO: Include build level


if __name__ == "__main__":
    ui = RigUI()
    ui.show()
