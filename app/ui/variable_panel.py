import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, messagebox
from app.ui.dialogs import AddVariableDialog, EditVariableDialog

class VariablePanel(ctk.CTkFrame):
    def __init__(self, master, var_manager, on_update_callback=None):
        super().__init__(master)
        self.var_manager = var_manager
        self.on_update_callback = on_update_callback

        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.init_ui()
        self.refresh_tree()

    def init_ui(self):
        # Search Bar
        self.search_input = ctk.CTkEntry(self, placeholder_text="Search variables...")
        self.search_input.grid(row=0, column=0, padx=5, pady=5, sticky="ew")
        self.search_input.bind("<KeyRelease>", self.filter_tree)

        # Treeview mapping CustomTkinter style
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Treeview",
                        background="#2b2b2b",
                        foreground="white",
                        fieldbackground="#2b2b2b",
                        borderwidth=0)
        style.map('Treeview', background=[('selected', '#1f538d')])

        self.tree = ttk.Treeview(self, columns=("Value",), show="tree headings")
        self.tree.heading("#0", text="Variables")
        self.tree.heading("Value", text="Value")
        self.tree.grid(row=1, column=0, padx=5, pady=0, sticky="nsew")

        self.tree.bind("<Double-1>", self.on_item_double_clicked)
        self.tree.bind("<Button-3>", self.show_context_menu) # right click

        # Add Button
        self.add_btn = ctk.CTkButton(self, text="+ Add Variable", command=self.add_variable)
        self.add_btn.grid(row=2, column=0, padx=5, pady=10, sticky="ew")

    def refresh_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        self.item_data = {}
        categorized = self.var_manager.get_variables_by_category()

        for category, variables in categorized.items():
            cat_id = self.tree.insert("", "end", text=category, open=True)
            for var in variables:
                var_id = self.tree.insert(cat_id, "end", text=var.display_name, values=(var.value,))
                self.item_data[var_id] = var

    def filter_tree(self, event):
        text = self.search_input.get().lower()
        # Since treeview doesn't support hiding easily, we rebuild it
        for item in self.tree.get_children():
            self.tree.delete(item)

        categorized = self.var_manager.get_variables_by_category()
        for category, variables in categorized.items():
            filtered_vars = [v for v in variables if text in v.display_name.lower() or text in v.value.lower()]
            if filtered_vars:
                cat_id = self.tree.insert("", "end", text=category, open=True)
                for var in filtered_vars:
                    var_id = self.tree.insert(cat_id, "end", text=var.display_name, values=(var.value,))
                    self.item_data[var_id] = var

    def show_context_menu(self, event):
        item_id = self.tree.identify_row(event.y)
        if item_id in self.item_data:
            self.tree.selection_set(item_id)
            menu = tk.Menu(self, tearoff=0)
            menu.add_command(label="Edit", command=lambda: self.edit_variable(self.item_data[item_id]))
            menu.add_command(label="Delete", command=lambda: self.delete_variable(self.item_data[item_id]))
            menu.post(event.x_root, event.y_root)

    def delete_variable(self, var):
        if messagebox.askyesno("Confirm", f"Delete {var.display_name}?"):
            self.var_manager.delete_variable(var.id)
            self.refresh_tree()
            if self.on_update_callback:
                self.on_update_callback()

    def on_item_double_clicked(self, event):
        item_id = self.tree.focus()
        if item_id in self.item_data:
            self.edit_variable(self.item_data[item_id])

    def add_variable(self):
        dialog = AddVariableDialog(self.winfo_toplevel())
        self.wait_window(dialog)
        data = dialog.get_data()
        if data and data.get('name') and data.get('value'):
            self.var_manager.add_variable(**data)
            self.refresh_tree()
            if self.on_update_callback:
                self.on_update_callback()

    def edit_variable(self, var):
        dialog = EditVariableDialog(var, self.winfo_toplevel())
        self.wait_window(dialog)
        new_val = dialog.get_new_value()
        if new_val is not None:
            self.var_manager.update_variable_value(var.id, new_val)
            self.refresh_tree()
            if self.on_update_callback:
                self.on_update_callback()
