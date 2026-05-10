import customtkinter as ctk
from app.utils.constants import DEFAULT_CATEGORIES

class AddVariableDialog(ctk.CTkToplevel):
    def __init__(self, parent=None, initial_value=""):
        super().__init__(parent)
        self.title("Add Variable")
        self.geometry("400x300")

        # Make modal
        if parent:
            self.transient(parent)

        self.result = None

        self.grid_columnconfigure(1, weight=1)

        # Name
        ctk.CTkLabel(self, text="Name (internal):").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.name_input = ctk.CTkEntry(self)
        self.name_input.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # Display Name
        ctk.CTkLabel(self, text="Display Name:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.disp_input = ctk.CTkEntry(self)
        self.disp_input.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Value
        ctk.CTkLabel(self, text="Current Value:").grid(row=2, column=0, padx=10, pady=10, sticky="e")
        self.val_input = ctk.CTkEntry(self)
        self.val_input.insert(0, initial_value)
        self.val_input.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

        # Category
        ctk.CTkLabel(self, text="Category:").grid(row=3, column=0, padx=10, pady=10, sticky="e")
        self.cat_input = ctk.CTkComboBox(self, values=DEFAULT_CATEGORIES)
        self.cat_input.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=4, column=0, columnspan=2, pady=20)

        ctk.CTkButton(btn_frame, text="Save", command=self.on_save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.on_cancel, fg_color="gray").pack(side="left", padx=10)

    def on_save(self):
        self.result = {
            'name': self.name_input.get().strip(),
            'display_name': self.disp_input.get().strip(),
            'value': self.val_input.get().strip(),
            'category': self.cat_input.get()
        }
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

    def get_data(self):
        return self.result

class EditVariableDialog(ctk.CTkToplevel):
    def __init__(self, variable, parent=None):
        super().__init__(parent)
        self.variable = variable
        self.title(f"Edit Variable: {variable.display_name}")
        self.geometry("400x200")

        if parent:
            self.transient(parent)

        self.result = None

        self.grid_columnconfigure(1, weight=1)

        # Value
        ctk.CTkLabel(self, text="New Value:").grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.val_input = ctk.CTkEntry(self)
        self.val_input.insert(0, variable.value)
        self.val_input.grid(row=0, column=1, padx=10, pady=10, sticky="ew")

        # History
        ctk.CTkLabel(self, text="History:").grid(row=1, column=0, padx=10, pady=10, sticky="e")
        hist = variable.history if variable.history else [""]
        self.hist_combo = ctk.CTkComboBox(self, values=hist, command=self._hist_changed)
        self.hist_combo.set(hist[-1] if hist else "")
        self.hist_combo.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        # Buttons
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, pady=20)

        ctk.CTkButton(btn_frame, text="Save", command=self.on_save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.on_cancel, fg_color="gray").pack(side="left", padx=10)

    def _hist_changed(self, text):
        self.val_input.delete(0, 'end')
        self.val_input.insert(0, text)

    def on_save(self):
        self.result = self.val_input.get().strip()
        self.destroy()

    def on_cancel(self):
        self.result = None
        self.destroy()

    def get_new_value(self):
        return self.result
