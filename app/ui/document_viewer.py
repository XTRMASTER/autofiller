import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTextEdit,
    QTableWidget, QTableWidgetItem, QSplitter,
    QLabel, QPushButton, QListWidget, QListWidgetItem,
    QFileDialog, QMessageBox
)
from PyQt6.QtCore import Qt
from app.core.document_processor import DocumentProcessor
from app.ui.extractor_dialog import ExtractorDialog

class DocumentViewer(QWidget):
    def __init__(self, doc_processor: DocumentProcessor, parent=None):
        super().__init__(parent)
        self.doc_processor = doc_processor
        self.current_template = None
        self.init_ui()

    def init_ui(self):
        main_layout = QHBoxLayout()

        splitter = QSplitter(Qt.Orientation.Horizontal)

        # Center Panel: Document View
        doc_panel = QWidget()
        doc_layout = QVBoxLayout(doc_panel)

        self.doc_label = QLabel("No document loaded.")
        doc_layout.addWidget(self.doc_label)

        self.word_view = QTextEdit()
        self.word_view.setReadOnly(True)
        self.word_view.hide()
        doc_layout.addWidget(self.word_view)

        self.excel_view = QTableWidget()
        self.excel_view.hide()
        doc_layout.addWidget(self.excel_view)

        splitter.addWidget(doc_panel)

        # Right Panel: Linked Variables & Actions
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        right_layout.addWidget(QLabel("Linked Variables:"))
        self.link_list = QListWidget()
        right_layout.addWidget(self.link_list)

        self.extract_btn = QPushButton("Extract Values from Text")
        self.extract_btn.clicked.connect(self.extract_values)
        self.extract_btn.setEnabled(False)
        right_layout.addWidget(self.extract_btn)

        self.apply_btn = QPushButton("Apply Variables & Save")
        self.apply_btn.clicked.connect(self.apply_variables)
        self.apply_btn.setEnabled(False)
        right_layout.addWidget(self.apply_btn)

        splitter.addWidget(right_panel)
        splitter.setSizes([700, 300])

        main_layout.addWidget(splitter)
        self.setLayout(main_layout)

    def load_document(self, filepath: str):
        try:
            template, content = self.doc_processor.process_document(filepath)
            self.current_template = template

            self.doc_label.setText(f"Document: {template.file_name}")

            # Auto link
            links = self.doc_processor.auto_link_variables(template.id, content)

            # Update UI
            if template.file_type == '.docx':
                self.show_word_view(content, links)
            elif template.file_type == '.xlsx':
                self.show_excel_view(content, links)

            self.refresh_links_list()
            self.apply_btn.setEnabled(True)
            self.extract_btn.setEnabled(True)

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to load document:\n{e}")

    def show_word_view(self, content, links):
        self.excel_view.hide()
        self.word_view.show()

        # Simple HTML render to highlight matched text
        html = ""
        link_texts = [l.match_text for l in links]

        for item in content:
            text = item.get('text', '')
            for lt in link_texts:
                if lt in text:
                    text = text.replace(lt, f"<span style='background-color: yellow;'>{lt}</span>")
            html += f"<p>{text}</p>"

        self.word_view.setHtml(html)

    def show_excel_view(self, content, links):
        self.word_view.hide()
        self.excel_view.show()
        self.excel_view.clear()

        # Simple list view of cells with content for MVP
        self.excel_view.setColumnCount(3)
        self.excel_view.setHorizontalHeaderLabels(["Sheet", "Cell", "Value"])
        self.excel_view.setRowCount(len(content))

        link_texts = [l.match_text for l in links]

        for i, item in enumerate(content):
            self.excel_view.setItem(i, 0, QTableWidgetItem(item.get('sheet', '')))
            self.excel_view.setItem(i, 1, QTableWidgetItem(item.get('address', '')))

            val_item = QTableWidgetItem(item.get('text', ''))

            # Highlight if matched
            for lt in link_texts:
                if lt in item.get('text', ''):
                    val_item.setBackground(Qt.GlobalColor.yellow)
                    break

            self.excel_view.setItem(i, 2, val_item)

        self.excel_view.resizeColumnsToContents()

    def refresh_links_list(self):
        self.link_list.clear()
        if not self.current_template: return

        links = self.doc_processor.db.get_links_for_template(self.current_template.id)
        variables = {v.id: v for v in self.doc_processor.db.get_variables()}

        for link in links:
            if link.variable_id in variables:
                var = variables[link.variable_id]
                item = QListWidgetItem(f"{var.display_name}: {var.value}")
                self.link_list.addItem(item)

    def apply_variables(self):
        if not self.current_template: return

        output_dir = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if not output_dir: return

        try:
            out_path = self.doc_processor.apply_variables_to_template(self.current_template.id, output_dir)
            QMessageBox.information(self, "Success", f"Document saved to:\n{out_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to apply variables:\n{e}")

    def extract_values(self):
        if not self.current_template: return

        # Get raw text from the view based on file type
        text = ""
        if self.current_template.file_type == '.docx':
            text = self.word_view.toPlainText()
        elif self.current_template.file_type == '.xlsx':
            for r in range(self.excel_view.rowCount()):
                item = self.excel_view.item(r, 2)
                if item: text += item.text() + " "

        if not text: return

        # Pass the var manager from main_window via parent chain
        var_manager = self.window().var_manager

        dialog = ExtractorDialog(text, var_manager, self)
        dialog.exec()

        # Refresh parent var panel if variable added
        self.window().var_panel.refresh_tree()
        self.refresh_links_list()
