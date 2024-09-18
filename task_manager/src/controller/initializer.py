from src.model.tasks import Tasks
from src.tasks_database.crud_database import get_tasks_excluding_status
#from .tasks_handler import TasksHandler

def initializer():
     ts = Tasks()
     tasks_dict = get_tasks_excluding_status('Done')
     ts.setup_tasks(tasks_dict)
