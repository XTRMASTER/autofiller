import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

class BatchProcessDialog(ctk.CTkToplevel):
    def __init__(self, db, doc_processor, parent=None):
        super().__init__(parent)
        self.db = db
        self.doc_processor = doc_processor
        self.title("Batch Process Templates")
        self.geometry("500x400")

        if parent:
            self.transient(parent)

        self.init_ui()
        self.load_templates()

    def init_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        ctk.CTkLabel(self, text="Select templates to process:").grid(row=0, column=0, padx=10, pady=5, sticky="w")

        self.listbox = tk.Listbox(self, selectmode="extended", bg="#2b2b2b", fg="white", selectbackground="#1f538d", borderwidth=0, highlightthickness=0)
        self.listbox.grid(row=1, column=0, padx=10, pady=5, sticky="nsew")

        self.progress = ctk.CTkProgressBar(self)
        self.progress.grid(row=2, column=0, padx=10, pady=10, sticky="ew")
        self.progress.set(0)

        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.grid(row=3, column=0, padx=10, pady=10)

        ctk.CTkButton(btn_frame, text="Process Selected", command=self.process_templates).pack(side="left", padx=5)
        ctk.CTkButton(btn_frame, text="Close", command=self.destroy, fg_color="gray").pack(side="left", padx=5)

    def load_templates(self):
        self.listbox.delete(0, 'end')
        templates = self.db.get_templates()
        for t in templates:
            self.listbox.insert('end', f"{t.id} - {t.file_name}")

    def process_templates(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "No templates selected.")
            return

        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return

        items = [self.listbox.get(i) for i in selection]
        template_ids = [int(item.split(' - ')[0]) for item in items]

        total = len(template_ids)

        self.progress.set(0)

        def worker():
            success_count = 0
            for i, tid in enumerate(template_ids):
                try:
                    self.doc_processor.apply_variables_to_template(tid, output_dir)
                    success_count += 1
                except Exception as e:
                    print(f"Failed to process {tid}: {e}")

                self.after(0, lambda progress=(i + 1) / total: self.progress.set(progress))

            self.after(0, lambda: messagebox.showinfo("Complete", f"Successfully processed {success_count} of {total} templates."))

        threading.Thread(target=worker, daemon=True).start()
