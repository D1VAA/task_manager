from dataclasses import dataclass
from datetime import date
from .tasks_storage import InvalidOperationError
from typing import Dict, Union


@dataclass
class Update:
    _description: str
    _creation_date: str
    update_id_db: int = 0

    @property
    def description(self):
        return self._description

    @property
    def creation_date(self):
        return self._creation_date

    @creation_date.setter
    def creation_date(self):
        raise InvalidOperationError('Creation date can\'t be changed.')


class UpdatesHandler:
    # Syntax: {task_id: { update_id: Update }}
    def __init__(self):
        self.updates: Dict[int, Dict[int, Update]] = {}

    def __gen_new_update_id(self, task_id: int) -> int | None:
        try:
            update_ids = self.updates[task_id].keys()
            return int(len(update_ids))+1

        except Exception as e:
            print(f"Error while generating a new update id: {e}")
            return

    def get_last_update(self, task_id):
        try:
            last_id: int = max(self.updates[task_id].keys())
            return self.updates[task_id][last_id]

        except Exception as e:
            print(f'Error occurred while searching the last update: {e}')

    def new_update(self, task_id: Union[str, int], description: str):
        if isinstance(task_id, str) and task_id.isdigit():
            task_id = int(task_id)

        elif isinstance(task_id, str) and not task_id.isdigit():
            raise ValueError("Task id is not a number.")

        if task_id not in self.updates.keys():
            self.updates[task_id] = {}

        new_id = self.__gen_new_update_id(task_id)
        creation_date = date.today().strftime('%d-%m-%Y')  # Format: dd-mm-yyyy
        self.updates[task_id][new_id] = Update(description, creation_date)

    def delete_update(self, task_id, update_id: Union[str, int]) -> None:
        del self.updates[int(task_id)][update_id]
