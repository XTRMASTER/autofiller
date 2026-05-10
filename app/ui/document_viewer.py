import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app.ui.extractor_dialog import ExtractorDialog

class DocumentViewer(ctk.CTkFrame):
    def __init__(self, master, doc_processor, parent_window=None):
        super().__init__(master)
        self.doc_processor = doc_processor
        self.parent_window = parent_window
        self.current_template = None

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        self.init_ui()

    def init_ui(self):
        # Left Panel: Doc Viewer
        self.viewer_frame = ctk.CTkFrame(self)
        self.viewer_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.viewer_frame.grid_rowconfigure(1, weight=1)
        self.viewer_frame.grid_columnconfigure(0, weight=1)

        self.doc_label = ctk.CTkLabel(self.viewer_frame, text="No document loaded.")
        self.doc_label.grid(row=0, column=0, pady=5, padx=5, sticky="w")

        self.word_view = ctk.CTkTextbox(self.viewer_frame, wrap="word")
        self.word_view.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.word_view.grid_remove() # hide initially

        self.excel_view = ttk.Treeview(self.viewer_frame, columns=("Sheet", "Cell", "Value"), show="headings")
        self.excel_view.heading("Sheet", text="Sheet")
        self.excel_view.heading("Cell", text="Cell")
        self.excel_view.heading("Value", text="Value")
        self.excel_view.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        self.excel_view.grid_remove() # hide initially

        # Right Panel: Links
        self.links_frame = ctk.CTkFrame(self)
        self.links_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.links_frame.grid_rowconfigure(1, weight=1)
        self.links_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.links_frame, text="Linked Variables:").grid(row=0, column=0, pady=5, sticky="w")

        self.link_list = tk.Listbox(self.links_frame, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.link_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.extract_btn = ctk.CTkButton(self.links_frame, text="Extract Values", command=self.extract_values, state="disabled")
        self.extract_btn.grid(row=2, column=0, pady=5, padx=5, sticky="ew")

        self.apply_btn = ctk.CTkButton(self.links_frame, text="Apply Variables & Save", command=self.apply_variables, state="disabled")
        self.apply_btn.grid(row=3, column=0, pady=10, padx=5, sticky="ew")

    def load_document(self, filepath):
        try:
            template, content = self.doc_processor.process_document(filepath)
            self.current_template = template
            self.doc_label.configure(text=f"Document: {template.file_name}")

            links = self.doc_processor.auto_link_variables(template.id, content)

            if template.file_type == '.docx':
                self.show_word_view(content, links)
            elif template.file_type == '.xlsx':
                self.show_excel_view(content, links)

            self.refresh_links_list()
            self.apply_btn.configure(state="normal")
            self.extract_btn.configure(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load document:\n{e}")

    def show_word_view(self, content, links):
        self.excel_view.grid_remove()
        self.word_view.grid()
        self.word_view.configure(state="normal")
        self.word_view.delete("1.0", "end")

        link_texts = [l.match_text for l in links]

        for item in content:
            text = item.get('text', '')
            self.word_view.insert("end", text + "\n\n")

        # Highlight tags
        self.word_view.tag_config("highlight", background="yellow", foreground="black")

        # Simple string matching highlight
        content_text = self.word_view.get("1.0", "end")
        for lt in link_texts:
            start_idx = "1.0"
            while True:
                start_idx = self.word_view.search(lt, start_idx, stopindex="end")
                if not start_idx: break
                end_idx = f"{start_idx}+{len(lt)}c"
                self.word_view.tag_add("highlight", start_idx, end_idx)
                start_idx = end_idx

        self.word_view.configure(state="disabled")

    def show_excel_view(self, content, links):
        self.word_view.grid_remove()
        self.excel_view.grid()

        for item in self.excel_view.get_children():
            self.excel_view.delete(item)

        link_texts = [l.match_text for l in links]

        for item in content:
            text = item.get('text', '')
            is_match = any(lt in text for lt in link_texts)

            tags = ("match",) if is_match else ()
            self.excel_view.insert("", "end", values=(item.get('sheet', ''), item.get('address', ''), text), tags=tags)

        self.excel_view.tag_configure("match", background="yellow", foreground="black")

    def refresh_links_list(self):
        self.link_list.delete(0, 'end')
        if not self.current_template: return

        links = self.doc_processor.db.get_links_for_template(self.current_template.id)
        variables = {v.id: v for v in self.doc_processor.db.get_variables()}

        for link in links:
            if link.variable_id in variables:
                var = variables[link.variable_id]
                self.link_list.insert('end', f"{var.display_name}: {var.value}")

    def extract_values(self):
        if not self.current_template: return

        text = ""
        if self.current_template.file_type == '.docx':
            text = self.word_view.get("1.0", "end")
        elif self.current_template.file_type == '.xlsx':
            for item in self.excel_view.get_children():
                text += str(self.excel_view.item(item, "values")[2]) + " "

        if not text.strip(): return

        dialog = ExtractorDialog(text, self.parent_window.var_manager, self.winfo_toplevel())
        self.wait_window(dialog)

        if self.parent_window and hasattr(self.parent_window, 'var_panel'):
            self.parent_window.var_panel.refresh_tree()
        self.refresh_links_list()

    def apply_variables(self):
        if not self.current_template: return

        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir: return

        try:
            out_path = self.doc_processor.apply_variables_to_template(self.current_template.id, output_dir)
            messagebox.showinfo("Success", f"Document saved to:\n{out_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to apply variables:\n{e}")
