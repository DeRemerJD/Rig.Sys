"""A dialog for adding a module to the rig."""

# TODO: Group the modules by type


from PySide2 import QtWidgets, QtCore

import rigsys.modules as rigsys_modules


class AddModuleDialog(QtWidgets.QDialog):
    """A dialog for adding a module to the rig."""

    def __init__(self):
        """Initialize the dialog."""
        super().__init__()

        self.selected_module = None

        self.setup_ui()

    def setup_ui(self):
        """Set up the UI for the dialog."""
        self.setWindowTitle("Add Module")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # Search bar
        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(self.search)
        self.main_layout.addWidget(self.search_bar)

        # Module list
        self.module_list = QtWidgets.QListWidget()
        self.module_list.itemClicked.connect(self.item_clicked)
        self.module_list.itemDoubleClicked.connect(self.accept)
        self.module_list.setAlternatingRowColors(True)
        self.main_layout.addWidget(self.module_list)

        self.fill_module_list()

        # Side selection
        self.radio_button_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.radio_button_layout)

        self.radio_button_layout.addWidget(QtWidgets.QLabel("Side: "))

        self.l_side_radio_button = QtWidgets.QRadioButton("L")
        self.l_side_radio_button.setChecked(True)
        self.radio_button_layout.addWidget(self.l_side_radio_button)

        self.m_side_radio_button = QtWidgets.QRadioButton("M")
        self.radio_button_layout.addWidget(self.m_side_radio_button)

        self.r_side_radio_button = QtWidgets.QRadioButton("R")
        self.radio_button_layout.addWidget(self.r_side_radio_button)

        # Module naming
        self.module_naming_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.module_naming_layout)

        self.module_name_line_edit = QtWidgets.QLineEdit()
        self.module_name_line_edit.setPlaceholderText("Module Name")
        self.module_naming_layout.addWidget(self.module_name_line_edit)

        # Accept/Cancel buttons
        self.button_layout = QtWidgets.QHBoxLayout()
        self.main_layout.addLayout(self.button_layout)

        self.accept_button = QtWidgets.QPushButton("Add")
        self.accept_button.clicked.connect(self.accept)
        self.accept_button.setDefault(True)
        self.accept_button.setEnabled(False)
        self.button_layout.addWidget(self.accept_button)

        self.cancel_button = QtWidgets.QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.button_layout.addWidget(self.cancel_button)

    def search(self):
        """Search the module list for the given text."""
        search_text = self.search_bar.text()

        for i in range(self.module_list.count()):
            item = self.module_list.item(i)
            if search_text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)

    def fill_module_list(self):
        """Fill the module list with modules."""
        modules_to_skip = ["MotionModuleBase", "ExportModuleBase", "UtilityModuleBase", "DeformerModuleBase"]

        for module_name, module in rigsys_modules.allModuleTypes.items():
            if module_name in modules_to_skip:
                continue

            item = QtWidgets.QListWidgetItem()
            item.setText(module_name)
            item.setSizeHint(QtCore.QSize(0, 25))

            self.module_list.addItem(item)
            item.setToolTip(module.__doc__)

    def item_clicked(self):
        """Handle a module being clicked."""
        self.accept_button.setEnabled(True)
        self.selected_module = self.module_list.currentItem().text()

        self.module_name_line_edit.setText(self.selected_module)

    def get_selected_side(self):
        """Get the currently selected side."""
        if self.l_side_radio_button.isChecked():
            return "L"
        elif self.m_side_radio_button.isChecked():
            return "M"
        elif self.r_side_radio_button.isChecked():
            return "R"

    def get_module_name(self):
        """Return the module name entered by the user."""
        return self.module_name_line_edit.text()
