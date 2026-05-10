import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from app.core.database import DatabaseManager
from app.core.variable_manager import VariableManager
from app.core.document_processor import DocumentProcessor
from app.ui.variable_panel import VariablePanel
from app.ui.presets_panel import PresetsPanel
from app.ui.document_viewer import DocumentViewer
from app.ui.batch_dialog import BatchProcessDialog

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
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=3)

        # Left Panel (Variables & Presets)
        self.left_frame = ctk.CTkFrame(self)
        self.left_frame.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        self.left_frame.grid_rowconfigure(0, weight=1)
        self.left_frame.grid_rowconfigure(1, weight=1)
        self.left_frame.grid_columnconfigure(0, weight=1)

        self.var_panel = VariablePanel(self.left_frame, self.var_manager, on_update_callback=self.on_variable_update)
        self.var_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 5))

        self.presets_panel = PresetsPanel(self.left_frame, self.db, self.var_manager, parent_window=self)
        self.presets_panel.grid(row=1, column=0, sticky="nsew", pady=(5, 0))

        # Right Panel (Document Viewer)
        self.doc_viewer = DocumentViewer(self, self.doc_processor, parent_window=self)
        self.doc_viewer.grid(row=0, column=1, sticky="nsew", padx=(0, 10), pady=10)

    def create_menu(self):
        # CustomTkinter doesn't have a native modern menubar, so we use standard tk.Menu
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
            self.doc_viewer.load_document(filepath)

    def open_batch_dialog(self):
        dialog = BatchProcessDialog(self.db, self.doc_processor, self)
        self.wait_window(dialog)
