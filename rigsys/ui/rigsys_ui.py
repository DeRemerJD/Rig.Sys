"""UI for rigsys."""


from PySide2 import QtWidgets, QtCore


class RigUI(QtWidgets.QWidget):
    """A UI for rigsys."""

    def __init__(self):
        """Initialize the UI."""
        super().__init__()

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
        print("Add module")

    def remove_module(self):
        """Remove a module from the rig."""
        print("Remove module")

    def build_rig(self):
        """Build the rig."""
        print("Build rig")


if __name__ == "__main__":
    ui = RigUI()
    ui.show()
