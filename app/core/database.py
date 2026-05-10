import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from app.utils.constants import DB_FILE
from app.models.data_models import Variable, Template, Link, Job, ShippingLine

class DatabaseManager:
    def __init__(self, db_path: str = DB_FILE):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        return sqlite3.connect(self.db_path)

    def init_db(self):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS variables (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE,
                display_name TEXT,
                value TEXT,
                category TEXT,
                history TEXT,
                created_at TIMESTAMP,
                updated_at TIMESTAMP
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS shipping_lines (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                code TEXT,
                address TEXT,
                gstin TEXT,
                contact TEXT,
                email TEXT,
                variables_json TEXT,
                created_at TIMESTAMP
            )
            """)
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                gstin TEXT,
                iec TEXT,
                address TEXT,
                email TEXT,
                variables_json TEXT
            )
            """)
            # Note: We add shipping_line_id to document_templates
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                file_name TEXT,
                file_type TEXT,
                shipping_line_id INTEGER,
                linked_variables_json TEXT,
                FOREIGN KEY (shipping_line_id) REFERENCES shipping_lines(id)
            )
            """)
            # Check if shipping_line_id exists in document_templates (for migration)
            cursor.execute("PRAGMA table_info(document_templates)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'shipping_line_id' not in columns:
                cursor.execute("ALTER TABLE document_templates ADD COLUMN shipping_line_id INTEGER REFERENCES shipping_lines(id)")

            cursor.execute("""
            CREATE TABLE IF NOT EXISTS links (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_id INTEGER,
                variable_id INTEGER,
                match_text TEXT,
                occurrence_index INTEGER,
                cell_address TEXT,
                paragraph_index INTEGER,
                FOREIGN KEY (template_id) REFERENCES document_templates(id),
                FOREIGN KEY (variable_id) REFERENCES variables(id)
            )
            """)

            # Note: jobs table needs shipping_line_id and selected_templates_json
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_name TEXT,
                shipping_line_id INTEGER,
                selected_templates_json TEXT,
                variables_snapshot_json TEXT,
                job_date TEXT,
                FOREIGN KEY (shipping_line_id) REFERENCES shipping_lines(id)
            )
            """)
            # Check for migration in jobs
            cursor.execute("PRAGMA table_info(jobs)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'shipping_line_id' not in columns:
                cursor.execute("ALTER TABLE jobs ADD COLUMN shipping_line_id INTEGER REFERENCES shipping_lines(id)")
            if 'selected_templates_json' not in columns:
                cursor.execute("ALTER TABLE jobs ADD COLUMN selected_templates_json TEXT DEFAULT '[]'")

            # check for migration in shipping_lines
            cursor.execute("PRAGMA table_info(shipping_lines)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'created_at' not in columns:
                cursor.execute("ALTER TABLE shipping_lines ADD COLUMN created_at TIMESTAMP")

            conn.commit()

    # --- Variables ---
    def create_variable(self, variable: Variable) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute("""
                INSERT INTO variables (name, display_name, value, category, history, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (variable.name, variable.display_name, variable.value, variable.category,
                  variable.history_json(), now, now))
            conn.commit()
            return cursor.lastrowid

    def get_variables(self) -> List[Variable]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM variables")
            rows = cursor.fetchall()
            return [Variable.from_db(row) for row in rows]

    def update_variable(self, variable: Variable):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute("""
                UPDATE variables
                SET display_name=?, value=?, category=?, history=?, updated_at=?
                WHERE id=?
            """, (variable.display_name, variable.value, variable.category,
                  variable.history_json(), now, variable.id))
            conn.commit()

    def delete_variable(self, variable_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM variables WHERE id=?", (variable_id,))
            cursor.execute("DELETE FROM links WHERE variable_id=?", (variable_id,))
            conn.commit()

    # --- Templates ---
    def add_template(self, template: Template) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO document_templates (file_path, file_name, file_type, shipping_line_id, linked_variables_json)
                VALUES (?, ?, ?, ?, ?)
            """, (template.file_path, template.file_name, template.file_type, template.shipping_line_id, template.linked_variables_json))
            conn.commit()
            return cursor.lastrowid

    def get_templates(self, shipping_line_id: Optional[int] = None) -> List[Template]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            if shipping_line_id is not None:
                cursor.execute("SELECT id, file_path, file_name, file_type, shipping_line_id, linked_variables_json FROM document_templates WHERE shipping_line_id=?", (shipping_line_id,))
            else:
                cursor.execute("SELECT id, file_path, file_name, file_type, shipping_line_id, linked_variables_json FROM document_templates")
            rows = cursor.fetchall()
            return [Template(id=row[0], file_path=row[1], file_name=row[2], file_type=row[3], shipping_line_id=row[4], linked_variables_json=row[5]) for row in rows]

    def delete_template(self, template_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM document_templates WHERE id=?", (template_id,))
            cursor.execute("DELETE FROM links WHERE template_id=?", (template_id,))
            conn.commit()

    # --- Links ---
    def create_link(self, link: Link) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO links (template_id, variable_id, match_text, occurrence_index, cell_address, paragraph_index)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (link.template_id, link.variable_id, link.match_text, link.occurrence_index, link.cell_address, link.paragraph_index))
            conn.commit()
            return cursor.lastrowid

    def get_links_for_template(self, template_id: int) -> List[Link]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM links WHERE template_id=?", (template_id,))
            rows = cursor.fetchall()
            return [Link(id=row[0], template_id=row[1], variable_id=row[2], match_text=row[3], occurrence_index=row[4], cell_address=row[5], paragraph_index=row[6]) for row in rows]

    def delete_link(self, link_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM links WHERE id=?", (link_id,))
            conn.commit()

    # --- Shipping Lines ---
    def get_shipping_lines(self) -> List[ShippingLine]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, code, contact, email, gstin, address, variables_json, created_at FROM shipping_lines")
            rows = cursor.fetchall()
            return [ShippingLine(id=row[0], name=row[1], code=row[2], contact=row[3], email=row[4], gstin=row[5], address=row[6], variables_json=row[7], created_at=row[8]) for row in rows]

    def add_shipping_line(self, sl: ShippingLine) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            now = datetime.now()
            cursor.execute("""
                INSERT INTO shipping_lines (name, code, contact, email, gstin, address, variables_json, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (sl.name, sl.code, sl.contact, sl.email, sl.gstin, sl.address, sl.variables_json, now))
            conn.commit()
            return cursor.lastrowid

    def update_shipping_line(self, sl: ShippingLine):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE shipping_lines
                SET name=?, code=?, contact=?, email=?, gstin=?, address=?, variables_json=?
                WHERE id=?
            """, (sl.name, sl.code, sl.contact, sl.email, sl.gstin, sl.address, sl.variables_json, sl.id))
            conn.commit()

    def delete_shipping_line(self, sl_id: int):
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM shipping_lines WHERE id=?", (sl_id,))
            conn.commit()
