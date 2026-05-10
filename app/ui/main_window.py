from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout, QSplitter,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

from app.core.database import DatabaseManager
from app.core.variable_manager import VariableManager
from app.core.document_processor import DocumentProcessor
from app.ui.variable_panel import VariablePanel
from app.ui.document_viewer import DocumentViewer
from app.ui.presets_panel import PresetsPanel
from app.utils.constants import SUPPORTED_EXTENSIONS

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("CHA Document Auto-Fill")
        self.resize(1200, 800)

        # Initialize Core
        self.db = DatabaseManager()
        self.var_manager = VariableManager(self.db)
        self.doc_processor = DocumentProcessor(self.db)

        self.init_ui()
        self.create_menus()

    def init_ui(self):
        central_widget = QWidget()
        main_layout = QHBoxLayout(central_widget)

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Left Panel: Variables & Presets
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self.var_panel = VariablePanel(self.var_manager)
        left_layout.addWidget(self.var_panel)

        self.presets_panel = PresetsPanel(self.db, self.var_manager)
        left_layout.addWidget(self.presets_panel)

        splitter.addWidget(left_panel)

        # Center/Right Panel: Document Viewer
        self.doc_viewer = DocumentViewer(self.doc_processor)
        splitter.addWidget(self.doc_viewer)

        # Connect signals
        self.var_panel.variable_updated.connect(self.doc_viewer.refresh_links_list)

        splitter.setSizes([300, 900])
        main_layout.addWidget(splitter)
        self.setCentralWidget(central_widget)

    def create_menus(self):
        menubar = self.menuBar()

        # File Menu
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open Template...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self.open_template)
        file_menu.addAction(open_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

    def open_template(self):
        filters = "Supported Files (*.docx *.xlsx);;Word Documents (*.docx);;Excel Files (*.xlsx)"
        filepath, _ = QFileDialog.getOpenFileName(self, "Open Template", "", filters)

        if filepath:
            self.doc_viewer.load_document(filepath)
