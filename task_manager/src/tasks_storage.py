from typing import Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import date


class InvalidOperationError(Exception):
    pass


@dataclass
class TaskObj:
    """
    Task structure.
    """
    name: str
    description: Optional[str]
    _creation_date: str  # Immutabel attribute
    task_id: int = 0
    _status: str = "Not Started"
    dependencies: list = field(default_factory=list)

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def status(self):
        return self._status

    @creation_date.setter
    def creation_date(self, _):
        raise InvalidOperationError("Creation Date can't be changed.")

    @status.setter
    def status(self, new_status):
        options = ["not started", "in progress", "done"]
        if new_status in options:
            self._status = new_status.title()
        else:
            raise ValueError("Invalid status option...")


class HandleTasks:
    """
    Class to manage tasks.
    """

    _tasks: Dict[int, TaskObj] = {}

    def __init__(self):
        self.id_counter = 0
        if self.tasks != {}:
            self.id_counter = max(self.tasks.keys())

    @property
    def tasks(self) -> Dict:
        """Get the dictionary of tasks."""
        return self._tasks

    @tasks.setter
    def tasks(self, value):
        self._tasks = value

    def __next_id(self) -> int:
        """Generate the next unique ID."""
        return len(self.tasks.keys()) + 1

    def new_task(self, name: str, description: Optional[str]) -> None:
        """
        Create a new task.
        """
        # Update the ID Counter
        self.id_counter: int = self.__next_id()
        creation_date = date.today().strftime("%d-%m-%Y")  # Format: dd-mm-yyyy

        self._tasks[self.id_counter] = TaskObj(
            name, description, creation_date)

    def _reorganize_tasks(self):
        """
        Reorganize the tasks dictionary to fill gaps in ID sequence.
        """
        new_tasks = {}
        for task_id, task in enumerate(self._tasks.values()):
            new_tasks[task_id + 1] = task  # Placeholder for deleted tasks
        self._tasks = new_tasks

    def delete_task(self, task_id: Union[str, int]) -> None:
        del self.tasks[int(task_id)]
        self._reorganize_tasks()

    def change_name(self, task_id, new_name):
        self.tasks[int(task_id)].name = new_name

    def change_description(self, task_id, new_desc):
        self.tasks[int(task_id)].description = new_desc

    def update_status(self, task_id, new_status):
        self.tasks[int(task_id)].status = new_status

    def create_dependencie(self, task_id, task_depend_id):
        self.tasks[int(task_id)].dependencies.append(task_depend_id)
