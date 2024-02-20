"""UI for rigsys.

TODO: Let user reorder modules

TODO: Let user save/load rigs (how are we going to do that?)

TODO: Let user save/load proxy positions

TODO: Grey out modules that won't be built at the current build level
"""


from PySide2 import QtWidgets, QtCore

from rigsys.ui.add_module_dialog import AddModuleDialog
from rigsys.ui.proceduralSettingsWidget.settingsWidget import SettingsWidget

import rigsys
import rigsys.modules as rigsys_modules

import json


class ObjectEncoder(json.JSONEncoder):
    def default(self, o):
        return {name: var for (name, var) in o.__dict__.items() if not str(name).startswith("_")}


class RigUI(QtWidgets.QWidget):
    """A UI for rigsys."""

    def __init__(self):
        """Initialize the UI."""
        super().__init__()

        self.rig = rigsys.Rig()
        self.build_level = -1

        self.setup_ui()

    def setup_ui(self):
        """Set up the UI."""
        self.setWindowTitle("RigSys UI")
        self.resize(800, 500)
        self.setMinimumHeight(400)
        self.setMinimumWidth(600)
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.WindowStaysOnTopHint)

        self.main_layout = QtWidgets.QVBoxLayout()
        self.setLayout(self.main_layout)

        # General settings
        self.general_settings_widget = QtWidgets.QWidget()
        self.general_settings_layout = QtWidgets.QVBoxLayout()
        self.general_settings_widget.setLayout(self.general_settings_layout)
        self.main_layout.addWidget(self.general_settings_widget)

        # Build order/Proxy build settings
        self.build_order_widget = QtWidgets.QWidget()
        self.build_order_layout = QtWidgets.QHBoxLayout()
        self.build_order_widget.setLayout(self.build_order_layout)

        build_level_label = QtWidgets.QLabel("Build Level")
        build_level_label.setFixedWidth(60)

        self.build_order_layout.addWidget(build_level_label)
        self.build_level_line_edit = QtWidgets.QLineEdit()
        self.build_level_line_edit.setFixedWidth(100)
        self.build_level_line_edit.setText("1")
        self.build_level_line_edit.textChanged.connect(self.on_build_level_changed)
        self.build_order_layout.addWidget(self.build_level_line_edit)

        self.build_proxies_only_checkbox = QtWidgets.QCheckBox("Build Proxies Only")
        self.build_order_layout.addWidget(self.build_proxies_only_checkbox)
        self.general_settings_layout.addWidget(self.build_order_widget)

        # Saved proxy settings
        self.proxy_settings_widget = QtWidgets.QWidget()
        self.proxy_settings_layout = QtWidgets.QHBoxLayout()
        self.proxy_settings_widget.setLayout(self.proxy_settings_layout)
        self.general_settings_layout.addWidget(self.proxy_settings_widget)

        self.proxy_settings_widget.setDisabled(True)  # TODO: Remove when it's working

        self.use_saved_proxy_positions_checkbox = QtWidgets.QCheckBox("Use Saved Proxy Positions")
        self.proxy_settings_layout.addWidget(self.use_saved_proxy_positions_checkbox)

        self.proxy_file_label = QtWidgets.QPushButton("Browse Proxy File (TODO)")
        self.proxy_settings_layout.addWidget(self.proxy_file_label)

        self.save_proxies_button = QtWidgets.QPushButton("Save Proxies")
        self.proxy_settings_layout.addWidget(self.save_proxies_button)

        # Splitter
        self.module_splitter = QtWidgets.QSplitter()
        self.module_splitter.splitterMoved.connect(self.module_splitter.saveState)
        self.module_splitter.setOrientation(QtCore.Qt.Horizontal)
        self.module_splitter.setOpaqueResize(False)
        self.main_layout.addWidget(self.module_splitter)
        # self.module_splitter.setSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Expanding)

        # Buttons setup
        self.buttons_widget = QtWidgets.QWidget()
        self.buttons_layout = QtWidgets.QHBoxLayout()
        self.buttons_layout.setAlignment(QtCore.Qt.AlignLeft)
        self.buttons_widget.setLayout(self.buttons_layout)

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

        # Module list
        self.module_list_widget_holder = QtWidgets.QWidget()
        self.module_list_layout = QtWidgets.QVBoxLayout()
        self.module_list_layout.setAlignment(QtCore.Qt.AlignTop)
        self.module_list_widget_holder.setLayout(self.module_list_layout)
        self.module_splitter.addWidget(self.module_list_widget_holder)

        self.module_list_widget = QtWidgets.QListWidget()
        self.module_list_widget.itemClicked.connect(self.on_module_clicked)
        self.module_list_widget.setAlternatingRowColors(True)
        self.module_list_layout.addWidget(self.buttons_widget)
        self.module_list_layout.addWidget(self.module_list_widget)

        # Module settings
        self.module_settings_widget_holder = QtWidgets.QWidget()
        self.module_settings_layout = QtWidgets.QVBoxLayout()
        self.module_settings_layout.setAlignment(QtCore.Qt.AlignTop)
        self.module_settings_widget_holder.setLayout(self.module_settings_layout)
        self.module_splitter.addWidget(self.module_settings_widget_holder)

        self.module_settings_layout.addWidget(QtWidgets.QLabel("Module Settings"))

        self.module_settings_widget = QtWidgets.QWidget()
        self.module_settings_layout.addWidget(self.module_settings_widget)

        # Build button
        self.build_button = QtWidgets.QPushButton("Build")
        self.build_button.setFixedHeight(50)
        self.build_button.clicked.connect(self.build_rig)
        self.main_layout.addWidget(self.build_button)

    # ----------------------------------------------- UI UPDATE FUNCTIONS ----------------------------------------------
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
        # If there's no selected module, return
        if not self.module_list_widget.selectedItems():
            return

        module_to_delete = self.module_list_widget.selectedItems()[0].text()
        list_item_to_delete = self.module_list_widget.selectedItems()[0]

        try:
            del self.rig.motionModules[module_to_delete]
            self.module_list_widget.takeItem(self.module_list_widget.row(list_item_to_delete))

        except KeyError:
            print(f"Module {module_to_delete} not found")
            return

    def build_rig(self):
        """Build the rig."""
        print("Building rig")

        print(json.dumps(self.rig, cls=ObjectEncoder, indent=4))

        build_proxies_only = self.build_proxies_only_checkbox.isChecked()
        use_saved_proxy_data = self.use_saved_proxy_positions_checkbox.isChecked()
        proxy_data_file = ""  # TODO: Fix when I get this actually working

        self.rig.build(buildLevel=self.build_level, buildProxiesOnly=build_proxies_only,
                       usedSavedProxyData=use_saved_proxy_data, proxyDataFile=proxy_data_file)

    def save_character_to_file(self):
        """Save the character to a python file.

        To do this, we'll need to grab
        - All modules
        - All editable params for each module

        Then format everything properly and write it to a file.
        """
        # TODO: Make UI to call this
        # TODO: Implement
        pass

    def on_build_level_changed(self):
        """Update the build level."""
        try:
            build_level = int(self.build_level_line_edit.text())
            self.rig.buildLevel = build_level
        except ValueError:
            print("Build level must be an integer")

        # TODO: Update the UI for any modules that won't be built at this build level
        # TODO: Highlight improper inputs in red

    def on_module_clicked(self):
        """Update the module settings when a module is clicked."""
        current_module_name = self.module_list_widget.currentItem().text()
        current_module = self.rig.motionModules[current_module_name]

        # Remove the old module_settings_widget
        self.module_settings_layout.removeWidget(self.module_settings_widget)
        # FIXME: Doesn't seem to properly remove the widget if there's a NumberInputWidget in it

        module_vars = current_module.baseEditableParameters() + current_module.customEditableParameters()
        self.module_settings_widget = SettingsWidget(
            inObject=current_module,
            variables=module_vars
        )
        self.module_settings_layout.addWidget(self.module_settings_widget)


if __name__ == "__main__":
    ui = RigUI()
    ui.show()
