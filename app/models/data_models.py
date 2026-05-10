from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional, Dict
import json

@dataclass
class Variable:
    id: Optional[int]
    name: str
    display_name: str
    value: str
    category: str
    history: List[str] = field(default_factory=list)
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def history_json(self) -> str:
        return json.dumps(self.history)

    @staticmethod
    def from_db(row: tuple):
        # id, name, display_name, value, category, history, created_at, updated_at
        hist = json.loads(row[5]) if row[5] else []
        return Variable(
            id=row[0],
            name=row[1],
            display_name=row[2],
            value=row[3],
            category=row[4],
            history=hist,
            created_at=row[6],
            updated_at=row[7]
        )

@dataclass
class Template:
    id: Optional[int]
    file_path: str
    file_name: str
    file_type: str
    linked_variables_json: str = "[]"

@dataclass
class Link:
    id: Optional[int]
    template_id: int
    variable_id: int
    match_text: str
    occurrence_index: int = 0
    cell_address: Optional[str] = None
    paragraph_index: Optional[int] = None

@dataclass
class Job:
    id: Optional[int]
    job_name: str
    job_date: str
    variables_snapshot_json: str
