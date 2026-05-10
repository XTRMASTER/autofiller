import json
from datetime import datetime
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
    QListWidget, QLabel, QInputDialog, QMessageBox, QTabWidget
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
        main_layout = QVBoxLayout(self)

        self.tabs = QTabWidget()

        # Tab 1: Master Data (Shipping Lines & Customers)
        master_tab = QWidget()
        master_layout = QHBoxLayout(master_tab)

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

        master_layout.addLayout(sl_layout)

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

        master_layout.addLayout(cust_layout)
        self.tabs.addTab(master_tab, "Master Data")

        # Tab 2: Jobs (Shipment Presets)
        jobs_tab = QWidget()
        jobs_layout = QVBoxLayout(jobs_tab)

        jobs_layout.addWidget(QLabel("Saved Jobs (Shipments):"))
        self.jobs_list = QListWidget()
        jobs_layout.addWidget(self.jobs_list)

        btn_layout = QHBoxLayout()
        self.add_job_btn = QPushButton("Save Current State as Job")
        self.add_job_btn.clicked.connect(self.add_job)
        btn_layout.addWidget(self.add_job_btn)

        self.load_job_btn = QPushButton("Load Job Variables")
        self.load_job_btn.clicked.connect(self.load_job)
        btn_layout.addWidget(self.load_job_btn)

        jobs_layout.addLayout(btn_layout)
        self.tabs.addTab(jobs_tab, "Jobs")

        main_layout.addWidget(self.tabs)

    def refresh_lists(self):
        self.sl_list.clear()
        self.cust_list.clear()
        self.jobs_list.clear()

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM shipping_lines")
            for row in cursor.fetchall():
                self.sl_list.addItem(f"{row[0]} - {row[1]}")

            cursor.execute("SELECT id, name FROM customers")
            for row in cursor.fetchall():
                self.cust_list.addItem(f"{row[0]} - {row[1]}")

            cursor.execute("SELECT id, job_name, job_date FROM jobs")
            for row in cursor.fetchall():
                self.jobs_list.addItem(f"{row[0]} - {row[1]} ({row[2]})")

    def add_shipping_line(self):
        name, ok = QInputDialog.getText(self, "Add Shipping Line", "Enter name:")
        if ok and name:
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

    def add_job(self):
        name, ok = QInputDialog.getText(self, "Save Job", "Enter Job ID/Name:")
        if ok and name:
            # Snapshot all variables
            current_vars = {v.name: v.value for v in self.var_manager.get_all_variables()}
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with self.db.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "INSERT INTO jobs (job_name, job_date, variables_snapshot_json) VALUES (?, ?, ?)",
                    (name, now, json.dumps(current_vars))
                )
                conn.commit()
            self.refresh_lists()

    def load_preset(self, table, list_widget, col_name):
        item = list_widget.currentItem()
        if not item: return

        preset_id = int(item.text().split(' - ')[0])
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT {col_name} FROM {table} WHERE id=?", (preset_id,))
            row = cursor.fetchone()
            if row and row[0]:
                vars_dict = json.loads(row[0])
                for name, value in vars_dict.items():
                    var = self.var_manager.find_variable_by_name(name)
                    if var:
                        self.var_manager.update_variable_value(var.id, value)
                QMessageBox.information(self, "Success", "Loaded variables.")

                # Signal main window to refresh panel if parent exposes it
                parent_win = self.window()
                if hasattr(parent_win, 'var_panel'):
                    parent_win.var_panel.refresh_tree()

    def load_shipping_line(self):
        self.load_preset("shipping_lines", self.sl_list, "variables_json")

    def load_customer(self):
        self.load_preset("customers", self.cust_list, "variables_json")

    def load_job(self):
        self.load_preset("jobs", self.jobs_list, "variables_snapshot_json")
