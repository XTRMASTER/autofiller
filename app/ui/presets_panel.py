import json
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QInputDialog, QMessageBox
)
from app.core.database import DatabaseManager
from app.core.variable_manager import VariableManager

class PresetsPanel(QWidget):
    def __init__(self, db: DatabaseManager, var_manager: VariableManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.var_manager = var_manager
        self.init_ui()
        self.refresh_lists()

    def init_ui(self):
        layout = QHBoxLayout(self)

        # Shipping Lines
        sl_layout = QVBoxLayout()
        sl_layout.addWidget(QLabel("Shipping Lines:"))
        self.sl_list = QListWidget()
        sl_layout.addWidget(self.sl_list)

        self.add_sl_btn = QPushButton("Add Shipping Line")
        self.add_sl_btn.clicked.connect(self.add_shipping_line)
        sl_layout.addWidget(self.add_sl_btn)

        self.load_sl_btn = QPushButton("Load Variables")
        self.load_sl_btn.clicked.connect(self.load_shipping_line)
        sl_layout.addWidget(self.load_sl_btn)

        layout.addLayout(sl_layout)

        # Customers
        cust_layout = QVBoxLayout()
        cust_layout.addWidget(QLabel("Customers:"))
        self.cust_list = QListWidget()
        cust_layout.addWidget(self.cust_list)

        self.add_cust_btn = QPushButton("Add Customer")
        self.add_cust_btn.clicked.connect(self.add_customer)
        cust_layout.addWidget(self.add_cust_btn)

        self.load_cust_btn = QPushButton("Load Variables")
        self.load_cust_btn.clicked.connect(self.load_customer)
        cust_layout.addWidget(self.load_cust_btn)

        layout.addLayout(cust_layout)

    def refresh_lists(self):
        self.sl_list.clear()
        self.cust_list.clear()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, variables_json FROM shipping_lines")
            for row in cursor.fetchall():
                self.sl_list.addItem(f"{row[0]} - {row[1]}")

            cursor.execute("SELECT id, name, variables_json FROM customers")
            for row in cursor.fetchall():
                self.cust_list.addItem(f"{row[0]} - {row[1]}")

    def add_shipping_line(self):
        name, ok = QInputDialog.getText(self, "Add Shipping Line", "Enter name:")
        if ok and name:
            # Snapshot current variables as preset
            current_vars = {v.name: v.value for v in self.var_manager.get_all_variables() if v.category == "Shipping Line"}
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO shipping_lines (name, variables_json) VALUES (?, ?)",
                    (name, json.dumps(current_vars))
                )
                conn.commit()
            self.refresh_lists()

    def add_customer(self):
        name, ok = QInputDialog.getText(self, "Add Customer", "Enter name:")
        if ok and name:
            current_vars = {v.name: v.value for v in self.var_manager.get_all_variables() if v.category == "Customer/GST"}
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO customers (name, variables_json) VALUES (?, ?)",
                    (name, json.dumps(current_vars))
                )
                conn.commit()
            self.refresh_lists()

    def load_preset(self, table, list_widget):
        item = list_widget.currentItem()
        if not item: return

        preset_id = int(item.text().split(' - ')[0])
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT variables_json FROM {table} WHERE id=?", (preset_id,))
            row = cursor.fetchone()
            if row and row[0]:
                vars_dict = json.loads(row[0])
                for name, value in vars_dict.items():
                    var = self.var_manager.find_variable_by_name(name)
                    if var:
                        self.var_manager.update_variable_value(var.id, value)
                QMessageBox.information(self, "Success", "Loaded preset variables.")

    def load_shipping_line(self):
        self.load_preset("shipping_lines", self.sl_list)

    def load_customer(self):
        self.load_preset("customers", self.cust_list)
