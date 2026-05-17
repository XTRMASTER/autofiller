import os
import customtkinter as ctk
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from app.ui.extractor_dialog import ExtractorDialog
import threading

class DocumentTab(ctk.CTkFrame):
    def __init__(self, master, template, content, links):
        super().__init__(master)
        self.template = template
        self.content = content
        self.links = links

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        if template.file_type == '.docx':
            self.word_view = ctk.CTkTextbox(self, wrap="word")
            self.word_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.show_word_view()
            self.excel_view = None
        elif template.file_type == '.xlsx':
            self.excel_view = ttk.Treeview(self, columns=("Sheet", "Cell", "Value"), show="headings")
            self.excel_view.heading("Sheet", text="Sheet")
            self.excel_view.heading("Cell", text="Cell")
            self.excel_view.heading("Value", text="Value")
            self.excel_view.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
            self.show_excel_view()
            self.word_view = None

    def show_word_view(self):
        self.word_view.configure(state="normal")
        self.word_view.delete("1.0", "end")

        link_texts = [link.match_text for link in self.links]

        for item in self.content:
            text = item.get('text', '')
            self.word_view.insert("end", text + "\n\n")

        self.word_view.tag_config("highlight", background="yellow", foreground="black")

        for lt in link_texts:
            start_idx = "1.0"
            while True:
                start_idx = self.word_view.search(lt, start_idx, stopindex="end")
                if not start_idx:
                    break
                end_idx = f"{start_idx}+{len(lt)}c"
                self.word_view.tag_add("highlight", start_idx, end_idx)
                start_idx = end_idx

        self.word_view.configure(state="disabled")

    def show_excel_view(self):
        for item in self.excel_view.get_children():
            self.excel_view.delete(item)

        link_texts = [link.match_text for link in self.links]

        for item in self.content:
            text = item.get('text', '')
            is_match = any(lt in text for lt in link_texts)
            tags = ("match",) if is_match else ()
            self.excel_view.insert("", "end", values=(item.get('sheet', ''), item.get('address', ''), text), tags=tags)

        self.excel_view.tag_configure("match", background="yellow", foreground="black")

    def get_text(self):
        if self.word_view:
            return self.word_view.get("1.0", "end")
        elif self.excel_view:
            text = ""
            for item in self.excel_view.get_children():
                text += str(self.excel_view.item(item, "values")[2]) + " "
            return text
        return ""


class DocumentViewer(ctk.CTkFrame):
    def __init__(self, master, doc_processor, parent_window=None):
        super().__init__(master)
        self.doc_processor = doc_processor
        self.parent_window = parent_window
        self.loaded_templates = {} # tid -> Template

        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=3)
        self.grid_columnconfigure(1, weight=1)

        self.init_ui()

    def init_ui(self):
        # Left Panel: Tabbed Doc Viewer
        self.viewer_frame = ctk.CTkFrame(self)
        self.viewer_frame.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)
        self.viewer_frame.grid_rowconfigure(0, weight=1)
        self.viewer_frame.grid_columnconfigure(0, weight=1)

        self.tabs = ctk.CTkTabview(self.viewer_frame)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=5, pady=5)

        # Right Panel: Links & Actions
        self.links_frame = ctk.CTkFrame(self)
        self.links_frame.grid(row=0, column=1, sticky="nsew", padx=5, pady=5)
        self.links_frame.grid_rowconfigure(1, weight=1)
        self.links_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(self.links_frame, text="Linked Variables (All Open Docs):").grid(row=0, column=0, pady=5, sticky="w")

        self.link_list = tk.Listbox(self.links_frame, bg="#2b2b2b", fg="white", borderwidth=0, highlightthickness=0)
        self.link_list.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)

        self.extract_btn = ctk.CTkButton(self.links_frame, text="Extract Values (Current Tab)", command=self.extract_values, state="disabled")
        self.extract_btn.grid(row=2, column=0, pady=5, padx=5, sticky="ew")

        self.apply_btn = ctk.CTkButton(self.links_frame, text="Apply Variables & Save All", command=self.apply_variables, state="disabled")
        self.apply_btn.grid(row=3, column=0, pady=10, padx=5, sticky="ew")

    def clear_documents(self):
        self.loaded_templates.clear()
        for tab_name in list(self.tabs._tab_dict.keys()):
            self.tabs.delete(tab_name)
        self.refresh_links_list()
        self.apply_btn.configure(state="disabled")
        self.extract_btn.configure(state="disabled")

    def load_document(self, filepath, template_id=None):
        try:
            if not template_id:
                template, content = self.doc_processor.process_document(filepath)
            else:
                # If loading from DB by ID, we still need to scan the content
                template = next((t for t in self.doc_processor.db.get_templates() if t.id == template_id), None)
                if not template:
                    raise ValueError("Template not found in DB")

                if template.file_type == '.docx':
                    from app.core.word_handler import WordHandler
                    content = WordHandler.scan_word_document(template.file_path)
                else:
                    from app.core.excel_handler import ExcelHandler
                    content = ExcelHandler.scan_excel_document(template.file_path)

            links = self.doc_processor.auto_link_variables(template.id, content)
            self.loaded_templates[template.id] = template

            # Create a tab for it
            tab_name = template.file_name
            # Ensure unique tab name if duplicates
            original_tab_name = tab_name
            count = 1
            while tab_name in self.tabs._tab_dict:
                tab_name = f"{original_tab_name} ({count})"
                count += 1

            tab = self.tabs.add(tab_name)
            tab.grid_columnconfigure(0, weight=1)
            tab.grid_rowconfigure(0, weight=1)

            # Store doc tab widget
            doc_tab = DocumentTab(tab, template, content, links)
            doc_tab.grid(row=0, column=0, sticky="nsew")

            self.refresh_links_list()
            self.apply_btn.configure(state="normal")
            self.extract_btn.configure(state="normal")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to load document:\n{e}")

    def refresh_links_list(self):
        self.link_list.delete(0, 'end')
        if not self.loaded_templates:
            return

        variables = {v.id: v for v in self.doc_processor.db.get_variables()}
        displayed_vars = set()

        for tid in self.loaded_templates.keys():
            links = self.doc_processor.db.get_links_for_template(tid)
            for link in links:
                if link.variable_id in variables and link.variable_id not in displayed_vars:
                    var = variables[link.variable_id]
                    self.link_list.insert('end', f"{var.display_name}: {var.value}")
                    displayed_vars.add(link.variable_id)

    def extract_values(self):
        current_tab_name = self.tabs.get()
        if not current_tab_name:
            return

        tab_frame = self.tabs.tab(current_tab_name)
        # Find DocumentTab child
        doc_tab = next(iter(tab_frame.winfo_children()))
        text = doc_tab.get_text()

        if not text.strip():
            return

        dialog = ExtractorDialog(text, self.parent_window.var_manager, self.winfo_toplevel())
        self.wait_window(dialog)

        if self.parent_window and hasattr(self.parent_window, 'var_panel'):
            self.parent_window.var_panel.refresh_tree()
        self.refresh_links_list()

    def apply_variables(self):
        if not self.loaded_templates:
            return

        output_dir = filedialog.askdirectory(title="Select Output Directory")
        if not output_dir:
            return

        job_prefix = ""
        # Ask for job prefix
        from customtkinter import CTkInputDialog
        dialog = CTkInputDialog(text="Enter an optional Job ID/Prefix for saved files (leave blank for none):", title="Job Prefix")
        job_prefix = dialog.get_input() or ""
        if job_prefix:
            job_prefix += "_"

        self.apply_btn.configure(state="disabled", text="Processing...")

        def worker():
            success_count = 0
            for tid, template in self.loaded_templates.items():
                try:
                    # Custom apply logic to handle custom filenames directly in processor isn't clean without refactoring processor.
                    # Since DocumentProcessor.apply_variables_to_template handles output, we will let it save as Updated_...
                    # and then rename it.
                    out_path = self.doc_processor.apply_variables_to_template(tid, output_dir)

                    if out_path and os.path.exists(out_path):
                        if job_prefix:
                            new_name = job_prefix + template.file_name
                            new_path = os.path.join(output_dir, new_name)
                            if os.path.exists(new_path):
                                os.remove(new_path)
                            os.rename(out_path, new_path)
                        success_count += 1
                except Exception as e:
                    self.after(0, lambda err=e, fname=template.file_name: messagebox.showerror("Error", f"Failed to apply to {fname}:\n{err}"))

            self.after(0, lambda: messagebox.showinfo("Success", f"Successfully processed and saved {success_count} documents."))
            self.after(0, lambda: self.apply_btn.configure(state="normal", text="Apply Variables & Save All"))

        threading.Thread(target=worker, daemon=True).start()
