from dataclasses import dataclass
from datetime import date
from .tasks_structure import InvalidOperationError
from typing import Dict, Union


@dataclass
class Update:
    _description: str
    _creation_date: str = ''
    update_id_db: int = 0

    def __post_init__(self):
        creation_date = date.today().strftime('%d-%m-%Y')  # Format: dd-mm-yyyy
        self._creation_date = creation_date

    @property
    def description(self):
        return self._description

    @property
    def creation_date(self):
        return self._creation_date

    @creation_date.setter
    def creation_date(self):
        raise InvalidOperationError('Creation date can\'t be changed.')