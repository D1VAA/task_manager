from typing import Optional
from dataclasses import dataclass, field


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
    updates: dict = field(default_factory=dict)
    dependencies: dict = field(default_factory=dict)
    depend_to: list = field(default_factory=list)

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
