"""A dialog for adding a module to the rig."""


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

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        self.search_bar = QtWidgets.QLineEdit()
        self.search_bar.setPlaceholderText("Search")
        self.search_bar.textChanged.connect(self.search)
        self.main_layout.addWidget(self.search_bar)

        self.module_list = QtWidgets.QListWidget()
        self.module_list.itemClicked.connect(self.item_clicked)
        self.module_list.itemDoubleClicked.connect(self.accept)
        self.module_list.setAlternatingRowColors(True)
        self.main_layout.addWidget(self.module_list)

        self.fill_module_list()

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
