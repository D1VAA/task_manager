from src.utils.imports import Dict, List
from dataclasses import dataclass, field
from src.model.tasks_structure import TaskObj
from src.utils.manage_temp_depend_file import get_all_depends, save_depend_at_temp_file

@dataclass
class Depends:
    """
    Estrutura das dependências.

    Args:
        main_task (TaskObj): Recebe o objeto task principal, ou seja, que vai possuir uma nova dependência.
        dependent_task (TaskObj): Recebe a task dependente, ou seja, que vai ser vinculada a outra task.
    """
    id: int = field(init=False)
    main_task: TaskObj
    dependent_task: TaskObj

    _id_counter: int = 0
    _existing_dependencies: set = field(default_factory=set)

    def __post_init__(self):
        if (self.main_task.task_id, self.dependent_task.task_id) in Depends._existing_dependencies:
            raise ValueError(f'Dependência entre {self.main_task.name} and {self.dependent_task.name} já existe!')

        Depends._id_counter += 1
        self.id = Depends._id_counter
        Depends._existing_dependencies.add((self.main_task.task_id, 
                                            self.dependent_task.task_id))

    @classmethod
    def remove_dependencie(cls, main_task: TaskObj, dependent_task: TaskObj) -> str:
        if (main_task.task_id, dependent_task.task_id) in cls._existing_dependencies:
            cls._existing_dependencies.remove((main_task.task_id, dependent_task.task_id))
            return 'Dependência removida com sucesso...'
        else:
            raise ValueError(f'Dependência entre {main_task.name} e {dependent_task.name} não existe.')
