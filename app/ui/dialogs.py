from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QComboBox, QPushButton, QMessageBox
)
from app.utils.constants import DEFAULT_CATEGORIES

class AddVariableDialog(QDialog):
    def __init__(self, parent=None, initial_value=""):
        super().__init__(parent)
        self.setWindowTitle("Add Variable")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        # Name
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel("Name (internal):"))
        self.name_input = QLineEdit()
        name_layout.addWidget(self.name_input)
        layout.addLayout(name_layout)

        # Display Name
        disp_layout = QHBoxLayout()
        disp_layout.addWidget(QLabel("Display Name:"))
        self.disp_input = QLineEdit()
        disp_layout.addWidget(self.disp_input)
        layout.addLayout(disp_layout)

        # Value
        val_layout = QHBoxLayout()
        val_layout.addWidget(QLabel("Current Value:"))
        self.val_input = QLineEdit(initial_value)
        val_layout.addWidget(self.val_input)
        layout.addLayout(val_layout)

        # Category
        cat_layout = QHBoxLayout()
        cat_layout.addWidget(QLabel("Category:"))
        self.cat_input = QComboBox()
        self.cat_input.addItems(DEFAULT_CATEGORIES)
        cat_layout.addWidget(self.cat_input)
        layout.addLayout(cat_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_data(self):
        return {
            'name': self.name_input.text().strip(),
            'display_name': self.disp_input.text().strip(),
            'value': self.val_input.text().strip(),
            'category': self.cat_input.currentText()
        }

class EditVariableDialog(QDialog):
    def __init__(self, variable, parent=None):
        super().__init__(parent)
        self.variable = variable
        self.setWindowTitle(f"Edit Variable: {variable.display_name}")
        self.setMinimumWidth(300)

        layout = QVBoxLayout()

        # Value
        val_layout = QHBoxLayout()
        val_layout.addWidget(QLabel("New Value:"))
        self.val_input = QLineEdit(variable.value)
        val_layout.addWidget(self.val_input)
        layout.addLayout(val_layout)

        # History
        hist_layout = QHBoxLayout()
        hist_layout.addWidget(QLabel("History:"))
        self.hist_combo = QComboBox()
        self.hist_combo.addItems(variable.history)
        self.hist_combo.currentTextChanged.connect(self._hist_changed)
        hist_layout.addWidget(self.hist_combo)
        layout.addLayout(hist_layout)

        # Buttons
        btn_layout = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self.reject)

        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def _hist_changed(self, text):
        self.val_input.setText(text)

    def get_new_value(self):
        return self.val_input.text().strip()
