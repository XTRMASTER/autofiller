from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QListWidget, QPushButton, QMessageBox, QListWidgetItem
)
from app.utils.helpers import extract_values_from_text
from app.core.variable_manager import VariableManager

class ExtractorDialog(QDialog):
    def __init__(self, text: str, var_manager: VariableManager, parent=None):
        super().__init__(parent)
        self.text = text
        self.var_manager = var_manager
        self.extracted_data = {}
        self.setWindowTitle("Extract Variables")
        self.setMinimumWidth(400)
        self.init_ui()
        self.extract()

    def init_ui(self):
        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Found the following possible values in document:"))
        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add Selected as Variable")
        self.add_btn.clicked.connect(self.add_selected)
        btn_layout.addWidget(self.add_btn)

        self.close_btn = QPushButton("Close")
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        layout.addLayout(btn_layout)

    def extract(self):
        self.extracted_data = extract_values_from_text(self.text)
        for category, values in self.extracted_data.items():
            for val in set(values): # unique
                item = QListWidgetItem(f"[{category}] {val}")
                item.setData(100, category)
                item.setData(101, val)
                self.list_widget.addItem(item)

    def add_selected(self):
        selected = self.list_widget.selectedItems()
        if not selected: return

        item = selected[0]
        category = item.data(100)
        value = item.data(101)

        from app.ui.dialogs import AddVariableDialog
        dialog = AddVariableDialog(self, initial_value=value)
        # Attempt to map to main categories
        if "GSTIN" in category:
            dialog.cat_input.setCurrentText("Customer/GST")

        if dialog.exec():
            data = dialog.get_data()
            if data['name'] and data['value']:
                self.var_manager.add_variable(**data)
                QMessageBox.information(self, "Success", "Variable added successfully.")
