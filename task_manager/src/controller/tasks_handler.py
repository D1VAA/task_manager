from src.model.tasks import TasksDict
from typing import Optional, Union
from datetime import date

from src.model.tasks_structure import TaskObj
from src.model.updates_strcuture import Update
from src.model.metaclass import Singleton


class TasksHandler(metaclass=Singleton):
    """
    Class to manage tasks objects.
    """

    _deleted_tasks = []

    def __init__(self):
        ts = TasksDict()
        self.tasks = ts.tasks
        self.id_counter = 0
        if self.tasks != {}:
            self.id_counter = max(self.tasks.keys())

    def __next_id(self) -> int:
        """Generate the next unique ID."""
        return len(self.tasks.keys()) + 1

    def get_update_obj(self, task_id, update_id):
        return self.tasks[task_id].updates[update_id]

    def get_dependencie_obj(self, task_id, dependent_task_id):
        return self.tasks[task_id].dependencies[dependent_task_id]

    def new_task(self, name: str, description: Optional[str]) -> None:
        """
        Create a new task.
        """
        # Update the ID Counter
        self.id_counter: int = self.__next_id()
        creation_date = date.today().strftime("%d-%m-%Y")  # Format: dd-mm-yyyy

        self.tasks[self.id_counter] = TaskObj(name, description, creation_date)

    def _reorganize_tasks(self):
        """
        Reorganize the tasks dictionary to fill gaps in ID sequence.
        """
        new_tasks = {}
        for task_id, task in enumerate(self.tasks.values()):
            new_tasks[task_id + 1] = task  # Placeholder for deleted tasks
        self.tasks = new_tasks

    def get_specific_db_id(self, local_id):
        return self.tasks[int(local_id)].id

    def delete_task(self, task_id: Union[str, int]) -> None:
        try:
            self._deleted_tasks.append(self.tasks[int(task_id)].id)
        except:
            ...
        del self.tasks[int(task_id)]
        self._reorganize_tasks()

    def change_name(self, task_id, new_name):
        self.tasks[int(task_id)].name = new_name

    def change_description(self, task_id, new_desc):
        self.tasks[int(task_id)].description = new_desc

    def update_status(self, task_id, new_status) -> str | None:
        if new_status == "done":
            depends = self.tasks[int(task_id)].dependencies.values()
            if any(x.status.lower() != "done" for x in depends):
                return f"Operação não realizada. A task {task_id} possui dependências não finalizadas.\n"

        self.tasks[int(task_id)].status = new_status

    def create_dependencie(self, task_id, task_depend_id):
        depend_obj = self.tasks[int(task_depend_id)]
        self.tasks[int(task_id)].dependencies[task_depend_id] = depend_obj

    def delete_dependencie(self, task_id, task_depend_id):
        self.tasks[int(task_id)].dependencies.pop(task_depend_id)
        # self.tasks[int(task_depend_id)].depend_to.remove(main_obj)

    def create_update(self, task_id, description):
        new_id = len(self.tasks[int(task_id)].updates.keys()) + 1
        self.tasks[int(task_id)].updates[new_id] = Update(description)

    def delete_update(self, task_id, update_id):
        self.tasks[int(task_id)].updates.pop(update_id)

