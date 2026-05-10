import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import json
from app.core.database import DatabaseManager
from app.core.variable_manager import VariableManager
from app.core.document_processor import DocumentProcessor
from app.ui.variable_panel import VariablePanel
from app.ui.presets_panel import PresetsPanel
from app.ui.document_viewer import DocumentViewer
from app.ui.batch_dialog import BatchProcessDialog
from app.ui.new_shipment_dialog import NewShipmentDialog

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("CHA Document Auto-Fill")
        self.geometry("1200x800")

        # Initialize Core
        self.db = DatabaseManager()
        self.var_manager = VariableManager(self.db)
        self.doc_processor = DocumentProcessor(self.db)

        self.init_ui()
        self.create_menu()

    def init_ui(self):
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

        # Top toolbar
        toolbar = ctk.CTkFrame(self, fg_color="transparent")
        toolbar.grid(row=0, column=0, columnspan=2, sticky="ew", padx=10, pady=5)

        # BIG New Shipment Button
        self.new_shipment_btn = ctk.CTkButton(
            toolbar, text="🚢 NEW SHIPMENT",
            command=self.open_new_shipment,
            font=("Arial", 16, "bold"),
            height=40
        )
        self.new_shipment_btn.pack(side="left", padx=5)

        # Left Panel (Variables & Presets)
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.var_panel = VariablePanel(self.left_frame, self.var_manager, on_update_callback=self.on_variable_update)
        self.var_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        self.presets_panel = PresetsPanel(self.left_frame, self.db, self.var_manager, parent_window=self)
        self.presets_panel.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        # Right Panel (Document Viewer)
        self.doc_viewer = DocumentViewer(self, self.doc_processor, parent_window=self)
        self.doc_viewer.grid(row=1, column=1, sticky="nsew", padx=(0, 10), pady=10)

    def create_menu(self):
        menubar = tk.Menu(self)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Open Template...", command=self.open_template, accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        batch_menu = tk.Menu(menubar, tearoff=0)
        batch_menu.add_command(label="Batch Process...", command=self.open_batch_dialog)
        menubar.add_cascade(label="Batch", menu=batch_menu)

        self.config(menu=menubar)
        self.bind("<Control-o>", lambda e: self.open_template())

    def on_variable_update(self):
        self.doc_viewer.refresh_links_list()

    def open_template(self):
        filetypes = (
            ('Supported Files', '*.docx *.xlsx'),
            ('Word Documents', '*.docx'),
            ('Excel Files', '*.xlsx'),
            ('All files', '*.*')
        )
        filepath = filedialog.askopenfilename(title="Open Template", filetypes=filetypes)

        if filepath:
            self.doc_viewer.clear_documents()
            self.doc_viewer.load_document(filepath)

    def open_batch_dialog(self):
        dialog = BatchProcessDialog(self.db, self.doc_processor, self)
        self.wait_window(dialog)

    def open_new_shipment(self):
        dialog = NewShipmentDialog(self.db, self)
        self.wait_window(dialog)

        if dialog.result_sl_id and dialog.result_template_ids:
            # 1. Clear current viewer
            self.doc_viewer.clear_documents()

            # 2. Auto-fill shipping line master details into explicit variables
            sls = self.db.get_shipping_lines()
            sl = next((s for s in sls if s.id == dialog.result_sl_id), None)
            if sl:
                # Explicitly map Master record fields to active variables
                master_map = {
                    "shipping_line_name": ("Shipping Line Name", sl.name),
                    "shipping_line_code": ("Shipping Line Code", sl.code),
                    "shipping_line_contact": ("Shipping Line Contact", sl.contact),
                    "shipping_line_email": ("Shipping Line Email", sl.email),
                    "shipping_line_gstin": ("Shipping Line GSTIN", sl.gstin),
                    "shipping_line_address": ("Shipping Line Address", sl.address)
                }

                for var_name, (disp_name, value) in master_map.items():
                    if value: # Only map if the master record has data for this field
                        var = self.var_manager.find_variable_by_name(var_name)
                        if var:
                            self.var_manager.update_variable_value(var.id, value)
                        else:
                            self.var_manager.add_variable(var_name, disp_name, value, "Shipping Line")

                # Also load any custom pre-saved SL variables from the JSON
                try:
                    vars_dict = json.loads(sl.variables_json)
                    for name, value in vars_dict.items():
                        var = self.var_manager.find_variable_by_name(name)
                        if var: self.var_manager.update_variable_value(var.id, value)
                except: pass

            # 3. Load all selected documents
            for tid in dialog.result_template_ids:
                templates = self.db.get_templates()
                template = next((t for t in templates if t.id == tid), None)
                if template and os.path.exists(template.file_path):
                    self.doc_viewer.load_document(template.file_path, template_id=template.id)
                elif template:
                    messagebox.showerror("Error", f"File not found for template {template.file_name}")

            self.var_panel.refresh_tree()
