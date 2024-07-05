from typing import Dict, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import date
from datetime import date

class InvalidOperationError(Exception):
    pass

class Status(Enum):
    """
    Default status options for tasks. (Kanban)
    """
    NOT_STARTED = 'Not Started'
    IN_PROGRESS = 'In Progress'
    DONE = 'Completed'

@dataclass
class Task:
    """
    Task structure.
    """
    name: str
    description: Optional[str]
    _creation_date: str  # Immutabel attribute
    _status: Status = "Not Started"

    @property
    def creation_date(self):
        return self._creation_date

    @property
    def status(self):
        return self._status
    
    @creation_date.setter
    def creation_date(self, _):
        raise InvalidOperationError('Creation Date can\'t be changed.')

    @status.setter
    def status(self, new_status):
        options = ['not started','in progress', 'done']
        if new_status in options:
            self._status = new_status.title()
        else:
            raise ValueError('Invalid status option...')
    
class HandleTasks:
    """
    Class to manage tasks.
    """
    id_counter = 0
    _tasks: Dict[int, Task] = {}
    def __init__(self):
        #self._tasks: Dict[int, Task] = {}  # Dictionary to store all Task instances with unique IDs.
        ...

    @property
    def tasks(self) -> Dict:
        """Get the dictionary of tasks."""
        return self._tasks
    
    @classmethod
    def __next_id(cls) -> int:
        """Generate the next unique ID."""
        cls.id_counter += 1
        next_id = cls.id_counter
        return next_id
    
    def new_task(self, name: str, description: Optional[str]) -> None:
        """
        Create a new task.
        """
        # Update the ID Counter
        id_counter: int = self.__next_id()
        creation_date = date.today().strftime('%d-%m-%Y')  # Format: dd-mm-yyyy

        self._tasks[id_counter] = Task(name, description, creation_date) 
