from .metaclass import Singleton


class TasksDict(metaclass=Singleton):
    """
    Class to manage tasks dictionary.
    """

    def __init__(self):
        self.instance = None
        self.tasks = {}

    def setup_tasks(self, new_dict):
        self.tasks = new_dict
