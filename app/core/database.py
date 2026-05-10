import sqlite3
import json
from datetime import datetime
from typing import List, Optional
from app.utils.constants import DB_FILE
from app.models.data_models import Variable, Template, Link, Job

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
                variables_json TEXT
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
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS document_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT,
                file_name TEXT,
                file_type TEXT,
                linked_variables_json TEXT
            )
            """)
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
            cursor.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                job_name TEXT,
                job_date TEXT,
                variables_snapshot_json TEXT
            )
            """)
            conn.commit()

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

    def add_template(self, template: Template) -> int:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO document_templates (file_path, file_name, file_type, linked_variables_json)
                VALUES (?, ?, ?, ?)
            """, (template.file_path, template.file_name, template.file_type, template.linked_variables_json))
            conn.commit()
            return cursor.lastrowid

    def get_templates(self) -> List[Template]:
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM document_templates")
            rows = cursor.fetchall()
            return [Template(id=row[0], file_path=row[1], file_name=row[2], file_type=row[3], linked_variables_json=row[4]) for row in rows]

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
