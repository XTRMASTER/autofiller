from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget,
    QTreeWidgetItem, QPushButton, QLineEdit, QMenu
)
from PyQt6.QtCore import Qt, pyqtSignal
from app.core.variable_manager import VariableManager
from app.ui.dialogs import AddVariableDialog, EditVariableDialog

class VariablePanel(QWidget):
    variable_updated = pyqtSignal()

    def __init__(self, var_manager: VariableManager, parent=None):
        super().__init__(parent)
        self.var_manager = var_manager
        self.init_ui()
        self.refresh_tree()

    def init_ui(self):
        layout = QVBoxLayout()

        # Search Bar
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search variables...")
        self.search_input.textChanged.connect(self.filter_tree)
        layout.addWidget(self.search_input)

        # Tree Widget
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(["Variables", "Value"])
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.show_context_menu)
        self.tree.itemDoubleClicked.connect(self.on_item_double_clicked)
        layout.addWidget(self.tree)

        # Add Button
        self.add_btn = QPushButton("+ Add Variable")
        self.add_btn.clicked.connect(self.add_variable)
        layout.addWidget(self.add_btn)

        self.setLayout(layout)

    def refresh_tree(self):
        self.tree.clear()
        categorized = self.var_manager.get_variables_by_category()

        for category, variables in categorized.items():
            cat_item = QTreeWidgetItem(self.tree, [category, ""])
            cat_item.setExpanded(True)
            for var in variables:
                var_item = QTreeWidgetItem(cat_item, [var.display_name, var.value])
                var_item.setData(0, Qt.ItemDataRole.UserRole, var)

    def filter_tree(self, text):
        text = text.lower()
        for i in range(self.tree.topLevelItemCount()):
            cat_item = self.tree.topLevelItem(i)
            cat_visible = False
            for j in range(cat_item.childCount()):
                var_item = cat_item.child(j)
                var = var_item.data(0, Qt.ItemDataRole.UserRole)
                if text in var.display_name.lower() or text in var.value.lower():
                    var_item.setHidden(False)
                    cat_visible = True
                else:
                    var_item.setHidden(True)
            cat_item.setHidden(not cat_visible)

    def show_context_menu(self, position):
        item = self.tree.itemAt(position)
        if item and item.parent(): # It's a variable, not a category
            var = item.data(0, Qt.ItemDataRole.UserRole)
            menu = QMenu()
            edit_action = menu.addAction("Edit")
            delete_action = menu.addAction("Delete")

            action = menu.exec(self.tree.viewport().mapToGlobal(position))
            if action == edit_action:
                self.edit_variable(var)
            elif action == delete_action:
                self.var_manager.delete_variable(var.id)
                self.refresh_tree()
                self.variable_updated.emit()

    def on_item_double_clicked(self, item, column):
        if item.parent():
            var = item.data(0, Qt.ItemDataRole.UserRole)
            self.edit_variable(var)

    def add_variable(self):
        dialog = AddVariableDialog(self)
        if dialog.exec():
            data = dialog.get_data()
            if data['name'] and data['value']:
                self.var_manager.add_variable(**data)
                self.refresh_tree()
                self.variable_updated.emit()

    def edit_variable(self, var):
        dialog = EditVariableDialog(var, self)
        if dialog.exec():
            new_val = dialog.get_new_value()
            self.var_manager.update_variable_value(var.id, new_val)
            self.refresh_tree()
            self.variable_updated.emit()
