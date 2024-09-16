from model.tasks import tasks
from typing import Dict, Optional, Union
from datetime import date

from model.tasks_structure import TaskObj
from model.updates_strcuture import Update

class TasksHandler:
    """
    Class to manage tasks.
    """
    def __init__(self):
        self.tasks = tasks
        self.id_counter = 0
        if tasks != {}:
            self.id_counter = max(tasks.keys())

    def __next_id(self) -> int:
        """Generate the next unique ID."""
        return len(tasks.keys()) + 1

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

    def get_specific_db_id(self, local_id):
        return tasks[int(local_id)].task_id
    
    def get_specific_local_id(self, db_id):
        db_id = int(db_id)
        for local_id, task in tasks.items():
            if task.task_id == db_id:
                return local_id

    def get_all_tasks_db_ids(self) -> Dict[int, TaskObj]:
        return {task.task_id: task for task in tasks.values()}
    
    def get_all_tasks_local_ids(self) -> Dict[int, TaskObj]:
        return {tid: task for tid, task in tasks.items()}

    def delete_task(self, task_id: Union[str, int]) -> None:
        del tasks[int(task_id)]
        self._reorganize_tasks()

    def change_name(self, task_id, new_name):
        tasks[int(task_id)].name = new_name

    def change_description(self, task_id, new_desc):
        tasks[int(task_id)].description = new_desc

    def update_status(self, task_id, new_status):
        tasks[int(task_id)].status = new_status

    def create_dependencie(self, task_id, task_depend_id):
        tasks[int(task_id)].dependencies.append(task_depend_id)

    def delete_dependencie(self, task_id, task_depend_id):
        tasks[int(task_id)].dependencies.remove(task_depend_id)

    def create_update(self, task_id, description):
        new_id = len(tasks[int(task_id)].updates.keys())+1
        tasks[int(task_id)].updates[new_id] = Update(description)

    def delete_update(self, task_id, update_id):
        tasks[int(task_id)].updates.pop(update_id)