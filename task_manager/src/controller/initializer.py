from src.model.tasks import TasksDict
from src.tasks_database.crud_database import get_tasks_excluding_status

class InitializationError(Exception):
    def __str__(self):
        return 'Erro ao initilizar o ambiente do programa. Gentileza verificar o código de inicialização.'

def initializer():
     try:
        ts = TasksDict()
        tasks_dict = get_tasks_excluding_status('Done')
        ts.setup_tasks(tasks_dict)
     except Exception:
        raise InitializationError()
