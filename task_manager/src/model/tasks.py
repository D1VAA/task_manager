class Tasks:
    """
    Class to manage tasks dictionary.
    """
    _instance = None
    _tasks = {}
    
    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance
    
    @property
    def tasks(self):
        return self._tasks
    
    def setup_tasks(self, new_dict):
        if isinstance(new_dict, dict):
            self._tasks = new_dict
    
    def get_tasks(self) -> dict:
        return self._tasks
