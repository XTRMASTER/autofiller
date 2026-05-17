from typing import List, Optional, Dict
from app.core.database import DatabaseManager
from app.models.data_models import Variable
from app.utils.constants import DEFAULT_CATEGORIES

class VariableManager:
    def __init__(self, db: DatabaseManager):
        self.db = db

    def get_all_variables(self) -> List[Variable]:
        return self.db.get_variables()

    def get_variables_by_category(self) -> Dict[str, List[Variable]]:
        variables = self.get_all_variables()
        categorized: Dict[str, List[Variable]] = {cat: [] for cat in DEFAULT_CATEGORIES}

        for v in variables:
            cat = v.category if v.category in categorized else "Other"
            if cat not in categorized:
                categorized[cat] = []
            categorized[cat].append(v)

        return categorized

    def add_variable(self, name: str, display_name: str, value: str, category: str) -> Variable:
        v = Variable(
            id=None,
            name=name,
            display_name=display_name,
            value=value,
            category=category,
            history=[value]
        )
        v.id = self.db.create_variable(v)
        return v

    def update_variable_value(self, variable_id: int, new_value: str) -> Optional[Variable]:
        variables = self.get_all_variables()
        for v in variables:
            if v.id == variable_id:
                if v.value != new_value:
                    if len(v.history) >= 5:
                        v.history.pop(0)
                    v.history.append(new_value)
                    v.value = new_value
                    self.db.update_variable(v)
                return v
        return None

    def delete_variable(self, variable_id: int):
        self.db.delete_variable(variable_id)

    def find_variable_by_name(self, name: str) -> Optional[Variable]:
        variables = self.get_all_variables()
        for v in variables:
            if v.name == name:
                return v
        return None
