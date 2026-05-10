import customtkinter as ctk
from tkinter import messagebox
from app.core.database import DatabaseManager

class NewShipmentDialog(ctk.CTkToplevel):
    def __init__(self, db: DatabaseManager, parent=None):
        super().__init__(parent)
        self.db = db
        self.title("New Import Shipment")
        self.geometry("500x500")
        if parent: self.transient(parent)

        self.result_sl_id = None
        self.result_template_ids = []

        self.shipping_lines = self.db.get_shipping_lines()
        self.sl_options = [f"{sl.id} - {sl.name}" for sl in self.shipping_lines]

        self.init_ui()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Shipping Line Dropdown
        sl_frame = ctk.CTkFrame(self, fg_color="transparent")
        sl_frame.grid(row=0, column=0, sticky="ew", padx=10, pady=10)

        ctk.CTkLabel(sl_frame, text="Shipping Line:").pack(side="left", padx=5)

        self.sl_combo = ctk.CTkComboBox(sl_frame, values=self.sl_options, command=self.on_sl_change)
        self.sl_combo.pack(side="left", fill="x", expand=True, padx=5)

        # Documents List
        ctk.CTkLabel(self, text="Select Documents:").grid(row=1, column=0, sticky="w", padx=10)

        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=5)

        # Select All/None Buttons
        sel_frame = ctk.CTkFrame(self, fg_color="transparent")
        sel_frame.grid(row=3, column=0, sticky="ew", padx=10, pady=5)
        ctk.CTkButton(sel_frame, text="Select All", command=lambda: self.toggle_all(True)).pack(side="left", padx=5)
        ctk.CTkButton(sel_frame, text="Select None", command=lambda: self.toggle_all(False)).pack(side="left", padx=5)

        # Bottom Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, pady=10)
        ctk.CTkButton(btn_frame, text="OK", command=self.on_ok).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, fg_color="gray").pack(side="left", padx=5)

        self.empty_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="⚠️ No templates linked to this shipping line.\nGo to Shipping Lines -> Manage Documents to add some.",
            text_color="#FFA500",
            font=("Arial", 12, "bold")
        )
        self.checkboxes = []

        # Load initially if available
        if self.sl_options:
            self.on_sl_change(self.sl_options[0])

    def on_sl_change(self, value):
        sl_id = int(value.split(' - ')[0])
        templates = self.db.get_templates(shipping_line_id=sl_id)

        # clear existing
        for cb, _ in self.checkboxes:
            cb.destroy()
        self.empty_label = ctk.CTkLabel(
            self.scrollable_frame,
            text="⚠️ No templates linked to this shipping line.\nGo to Shipping Lines -> Manage Documents to add some.",
            text_color="#FFA500",
            font=("Arial", 12, "bold")
        )
        self.checkboxes = []

        for i, t in enumerate(templates):
            cb = ctk.CTkCheckBox(self.scrollable_frame, text=t.file_name)
            cb.grid(row=i, column=0, sticky="w", pady=5)
            cb.select() # Default all checked
            self.checkboxes.append((cb, t.id))

    def toggle_all(self, state):
        for cb, _ in self.checkboxes:
            if state: cb.select()
            else: cb.deselect()

    def on_ok(self):
        if not self.sl_combo.get():
            messagebox.showwarning("Warning", "Select a Shipping Line.")
            return

        self.result_sl_id = int(self.sl_combo.get().split(' - ')[0])
        self.result_template_ids = [tid for cb, tid in self.checkboxes if cb.get() == 1]

        self.destroy()
