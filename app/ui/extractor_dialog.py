import customtkinter as ctk
from tkinter import messagebox
import tkinter as tk
from app.utils.helpers import extract_values_from_text

class ExtractorDialog(ctk.CTkToplevel):
    def __init__(self, text: str, var_manager, parent=None):
        super().__init__(parent)
        self.text = text
        self.var_manager = var_manager
        self.title("Extract Variables")
        self.geometry("500x400")

        if parent:
            self.transient(parent)

        from typing import Dict
        self.extracted_data: Dict[str, str] = {}
        self.init_ui()
        self.extract()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Found the following possible values in document:").grid(row=0, column=0, padx=10, pady=10, sticky="w")

        # We need a Listbox, CTk doesn't have a native list widget, so we use tk.Listbox with some styling
        self.listbox = tk.Listbox(self, bg="#2b2b2b", fg="white", selectbackground="#1f538d", borderwidth=0, highlightthickness=0)
        self.listbox.grid(row=1, column=0, padx=10, pady=0, sticky="nsew")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, padx=10, pady=10)

        ctk.CTkButton(btn_frame, text="Add Selected as Variable", command=self.add_selected).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Close", command=self.destroy, fg_color="gray").pack(side="left", padx=5)

    def extract(self):
        self.extracted_data = extract_values_from_text(self.text)
        self.items_data = [] # Store underlying data matching listbox index

        for category, values in self.extracted_data.items():
            for val in set(values): # unique
                display_text = f"[{category}] {val}"
                self.listbox.insert("end", display_text)
                self.items_data.append({"category": category, "value": val})

    def add_selected(self):
        selection = self.listbox.curselection()
        if not selection:
            return

        idx = selection[0]
        data = self.items_data[idx]

        from app.ui.dialogs import AddVariableDialog
        dialog = AddVariableDialog(self, initial_value=data["value"])
        if "GSTIN" in data["category"]:
            dialog.cat_input.set("Customer/GST")

        self.wait_window(dialog)

        result = dialog.get_data()
        if result and result.get('name') and result.get('value'):
            self.var_manager.add_variable(**result)
            messagebox.showinfo("Success", "Variable added successfully.")
