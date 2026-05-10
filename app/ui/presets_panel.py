import json
from datetime import datetime
import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

class PresetsPanel(ctk.CTkFrame):
    def __init__(self, master, db, var_manager, parent_window=None):
        super().__init__(master)
        self.db = db
        self.var_manager = var_manager
        self.parent_window = parent_window

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.init_ui()
        self.refresh_lists()

    def init_ui(self):
        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        self.tabs.add("Master Data")
        self.tabs.add("Jobs")

        # --- Master Data Tab ---
        tab1 = self.tabs.tab("Master Data")
        tab1.grid_columnconfigure((0, 1), weight=1)
        tab1.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tab1, text="Shipping Lines:").grid(row=0, column=0, sticky="w")
        self.sl_list = tk.Listbox(tab1, bg="#2b2b2b", fg="white", selectbackground="#1f538d", borderwidth=0, highlightthickness=0)
        self.sl_list.grid(row=1, column=0, sticky="nsew", padx=2)

        ctk.CTkLabel(tab1, text="Customers:").grid(row=0, column=1, sticky="w")
        self.cust_list = tk.Listbox(tab1, bg="#2b2b2b", fg="white", selectbackground="#1f538d", borderwidth=0, highlightthickness=0)
        self.cust_list.grid(row=1, column=1, sticky="nsew", padx=2)

        btn_frame1 = ctk.CTkFrame(tab1, fg_color="transparent")
        btn_frame1.grid(row=2, column=0, pady=5)
        ctk.CTkButton(btn_frame1, text="+ Add", command=self.add_shipping_line, width=60).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame1, text="Load", command=self.load_shipping_line, width=60).pack(side="left", padx=2)

        btn_frame2 = ctk.CTkFrame(tab1, fg_color="transparent")
        btn_frame2.grid(row=2, column=1, pady=5)
        ctk.CTkButton(btn_frame2, text="+ Add", command=self.add_customer, width=60).pack(side="left", padx=2)
        ctk.CTkButton(btn_frame2, text="Load", command=self.load_customer, width=60).pack(side="left", padx=2)

        # --- Jobs Tab ---
        tab2 = self.tabs.tab("Jobs")
        tab2.grid_columnconfigure(0, weight=1)
        tab2.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(tab2, text="Saved Jobs (Shipments):").grid(row=0, column=0, sticky="w")
        self.jobs_list = tk.Listbox(tab2, bg="#2b2b2b", fg="white", selectbackground="#1f538d", borderwidth=0, highlightthickness=0)
        self.jobs_list.grid(row=1, column=0, sticky="nsew", pady=2)

        btn_frame3 = ctk.CTkFrame(tab2, fg_color="transparent")
        btn_frame3.grid(row=2, column=0, pady=5)
        ctk.CTkButton(btn_frame3, text="Save Job", command=self.add_job).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame3, text="Load Job", command=self.load_job).pack(side="left", padx=5)

    def refresh_lists(self):
        self.sl_list.delete(0, 'end')
        self.cust_list.delete(0, 'end')
        self.jobs_list.delete(0, 'end')

        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name FROM shipping_lines")
            for row in cursor.fetchall():
                self.sl_list.insert('end', f"{row[0]} - {row[1]}")

            cursor.execute("SELECT id, name FROM customers")
            for row in cursor.fetchall():
                self.cust_list.insert('end', f"{row[0]} - {row[1]}")

            cursor.execute("SELECT id, job_name, job_date FROM jobs")
            for row in cursor.fetchall():
                self.jobs_list.insert('end', f"{row[0]} - {row[1]} ({row[2]})")

    def simple_input(self, title, prompt):
        dialog = ctk.CTkInputDialog(text=prompt, title=title)
        return dialog.get_input()

    def add_shipping_line(self):
        name = self.simple_input("Add Shipping Line", "Enter name:")
        if name:
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
        name = self.simple_input("Add Customer", "Enter name:")
        if name:
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
        name = self.simple_input("Save Job", "Enter Job ID/Name:")
        if name:
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

    def load_preset(self, table, listbox, col_name):
        selection = listbox.curselection()
        if not selection: return

        item_text = listbox.get(selection[0])
        preset_id = int(item_text.split(' - ')[0])

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
                messagebox.showinfo("Success", "Loaded variables.")

                if self.parent_window and hasattr(self.parent_window, 'var_panel'):
                    self.parent_window.var_panel.refresh_tree()

    def load_shipping_line(self):
        self.load_preset("shipping_lines", self.sl_list, "variables_json")

    def load_customer(self):
        self.load_preset("customers", self.cust_list, "variables_json")

    def load_job(self):
        self.load_preset("jobs", self.jobs_list, "variables_snapshot_json")
