import os
import json
from typing import List, Dict, Tuple
from app.core.database import DatabaseManager
from app.core.word_handler import WordHandler
from app.core.excel_handler import ExcelHandler
from app.models.data_models import Template, Link, Variable

class DocumentProcessor:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def process_document(self, filepath: str) -> Tuple[Template, List[dict]]:
        """
        Detects file type, scans it, adds it to DB, and returns the template and scan results.
        """
        filename = os.path.basename(filepath)
        ext = os.path.splitext(filename)[1].lower()

        content = []
        if ext == '.docx':
            content = WordHandler.scan_word_document(filepath)
        elif ext == '.xlsx':
            content = ExcelHandler.scan_excel_document(filepath)
        else:
            raise ValueError(f"Unsupported file type: {ext}")

        template = Template(
            id=None,
            file_path=filepath,
            file_name=filename,
            file_type=ext
        )
        template.id = self.db.add_template(template)

        return template, content

    def auto_link_variables(self, template_id: int, content: List[dict]) -> List[Link]:
        """
        Scans content against existing variables and creates links for matches.
        """
        variables = self.db.get_variables()
        links = []

        for item in content:
            text = item.get('text', '')
            for var in variables:
                if var.value and var.value in text:
                    link = Link(
                        id=None,
                        template_id=template_id,
                        variable_id=var.id,
                        match_text=var.value,
                        occurrence_index=item.get('index', 0),
                        cell_address=item.get('address'),
                        paragraph_index=item.get('index') if item.get('type') == 'paragraph' else None
                    )
                    link.id = self.db.create_link(link)
                    links.append(link)
        return links

    def apply_variables_to_template(self, template_id: int, output_dir: str) -> str:
        """
        Applies current variable values to the linked template and saves to output directory.
        """
        templates = self.db.get_templates()
        template = next((t for t in templates if t.id == template_id), None)
        if not template:
            raise ValueError(f"Template with id {template_id} not found.")

        links = self.db.get_links_for_template(template_id)
        variables = {v.id: v for v in self.db.get_variables()}

        # Build replacement dict
        replacements = {}
        for link in links:
            if link.variable_id in variables:
                var = variables[link.variable_id]
                replacements[link.match_text] = var.value

        if not replacements:
            return template.file_path # No changes needed

        output_filename = f"Updated_{template.file_name}"
        output_path = os.path.join(output_dir, output_filename)

        if template.file_type == '.docx':
            WordHandler.apply_word_variables(template.file_path, replacements, output_path)
        elif template.file_type == '.xlsx':
            ExcelHandler.apply_excel_variables(template.file_path, replacements, output_path)

        return output_path

    def batch_apply(self, template_ids: List[int], output_dir: str) -> List[str]:
        output_paths = []
        for tid in template_ids:
            try:
                out_path = self.apply_variables_to_template(tid, output_dir)
                output_paths.append(out_path)
            except Exception as e:
                print(f"Error applying template {tid}: {e}")
        return output_paths
