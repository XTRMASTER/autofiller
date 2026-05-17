import docx
import os

class WordHandler:
    @staticmethod
    def scan_word_document(filepath: str):
        """
        Scans a Word document and returns its paragraphs and text content.
        This is a basic implementation that reads text from paragraphs and tables.
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"File not found: {filepath}")

        doc = docx.Document(filepath)
        content = []
        for i, para in enumerate(doc.paragraphs):
            if para.text.strip():
                content.append({'type': 'paragraph', 'index': i, 'text': para.text})

        for i, table in enumerate(doc.tables):
            for row_idx, row in enumerate(table.rows):
                for col_idx, cell in enumerate(row.cells):
                    if cell.text.strip():
                        content.append({
                            'type': 'table_cell',
                            'table_idx': i,
                            'row_idx': row_idx,
                            'col_idx': col_idx,
                            'text': cell.text
                        })
        return content

    @staticmethod
    def apply_word_variables(filepath: str, variables_dict: dict, output_path: str):
        """
        Replaces variables in a Word document and saves to output_path.
        variables_dict maps text to replace to the new value.
        Preserves simple formatting by replacing text within runs.
        """
        doc = docx.Document(filepath)

        # Replace in paragraphs
        for para in doc.paragraphs:
            WordHandler._replace_in_paragraph(para, variables_dict)

        # Replace in tables
        for table in doc.tables:
            for row in table.rows:
                for cell in row.cells:
                    for para in cell.paragraphs:
                        WordHandler._replace_in_paragraph(para, variables_dict)

        doc.save(output_path)

    @staticmethod
    def _replace_in_paragraph(para, variables_dict):
        # We perform replacements at the run level to preserve original formatting.
        # This approach replaces full matches that exist within a single run,
        # which covers the vast majority of simple templates.
        for run in para.runs:
            for old_val, new_val in variables_dict.items():
                if old_val in run.text:
                    run.text = run.text.replace(old_val, new_val)
