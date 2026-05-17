import customtkinter as ctk
from tkinter import filedialog, messagebox
import os
from app.models.data_models import ShippingLine, Template

from typing import Optional

class ShippingLineDialog(ctk.CTkToplevel):
    def __init__(self, parent=None, sl: Optional[ShippingLine]=None):
        super().__init__(parent)
        self.title("Shipping Line Details")
        self.geometry("450x400")
        if parent:
            self.transient(parent)

        self.result = None
        self.sl = sl

        self.grid_columnconfigure(1, weight=1)

        fields = [("Name:", "name"), ("Code:", "code"), ("Contact:", "contact"),
                  ("Email:", "email"), ("GSTIN:", "gstin"), ("Address:", "address")]

        self.inputs = {}
        for i, (label_text, key) in enumerate(fields):
            ctk.CTkLabel(self, text=label_text).grid(row=i, column=0, padx=10, pady=5, sticky="e")
            entry = ctk.CTkEntry(self)
            entry.grid(row=i, column=1, padx=10, pady=5, sticky="ew")
            if self.sl and getattr(self.sl, key):
                entry.insert(0, getattr(self.sl, key))
            self.inputs[key] = entry

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=len(fields), column=0, columnspan=2, pady=20)

        ctk.CTkButton(btn_frame, text="Save", command=self.on_save).pack(side="left", padx=10)
        ctk.CTkButton(btn_frame, text="Cancel", command=self.destroy, fg_color="gray").pack(side="left", padx=10)

    def on_save(self):
        data = {k: v.get().strip() for k, v in self.inputs.items()}
        if not data["name"]:
            messagebox.showwarning("Warning", "Name is required")
            return

        if self.sl:
            for k, v in data.items():
                setattr(self.sl, k, v)
            self.result = self.sl
        else:
            self.result = ShippingLine(id=None, variables_json="{}", created_at=None, **data)

        self.destroy()

class ManageDocumentsDialog(ctk.CTkToplevel):
    def __init__(self, sl: ShippingLine, db, parent=None):
        super().__init__(parent)
        self.sl = sl
        self.db = db
        self.title(f"Manage Documents - {sl.name}")
        self.geometry("500x400")
        if parent:
            self.transient(parent)

        self.init_ui()
        self.load_docs()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text=f"Templates for {self.sl.name}:").grid(row=0, column=0, padx=10, pady=5, sticky="w")

        import tkinter as tk
        self.listbox = tk.Listbox(self, bg="#2b2b2b", fg="white", selectbackground="#1f538d", borderwidth=0, highlightthickness=0)
        self.listbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=2, column=0, pady=10)

        ctk.CTkButton(btn_frame, text="Add Template", command=self.add_doc).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Remove Selected", command=self.remove_doc).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Close", command=self.destroy, fg_color="gray").pack(side="left", padx=5)

    def load_docs(self):
        self.listbox.delete(0, 'end')
        self.templates = self.db.get_templates(shipping_line_id=self.sl.id)
        for t in self.templates:
            status = "" if os.path.exists(t.file_path) else " [FILE NOT FOUND]"
            self.listbox.insert('end', f"{t.id} - {t.file_name}{status}")
            if status:
                self.listbox.itemconfig('end', {'fg': 'red'})

    def add_doc(self):
        filetypes = (('Word/Excel', '*.docx *.xlsx'), ('All files', '*.*'))
        filepath = filedialog.askopenfilename(title="Select Template", filetypes=filetypes)
        if filepath:
            filename = os.path.basename(filepath)
            ext = os.path.splitext(filename)[1].lower()
            t = Template(id=None, file_path=filepath, file_name=filename, file_type=ext, shipping_line_id=self.sl.id)
            self.db.add_template(t)
            self.load_docs()

    def remove_doc(self):
        selection = self.listbox.curselection()
        if not selection:
            return
        item_text = self.listbox.get(selection[0])
        tid = int(item_text.split(' - ')[0])

        if messagebox.askyesno("Confirm", "Remove this template?"):
            self.db.delete_template(tid)
            self.load_docs()
