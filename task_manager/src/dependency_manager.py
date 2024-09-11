from utils.imports import Dict, List
from dataclasses import dataclass, field
from tasks_storage import TaskObj
from utils.manage_temp_depend_file import get_all_depends, save_depend_at_temp_file

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
    _existing_dependencies: set = set()

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

class DependencieHandler:
    """
    Classe para fazer todo o gerenciamento das dependências entre as tasks.
    Os IDs armazenados são os IDs das tasks no banco de dados. Não os IDs locais.
    """
    _depends: Dict[int, Depends] = {}
    @property
    def dependencies(self) -> Dict:
        return self._depends

    def create_dependencie(self, main_task: TaskObj, 
                           dependent_task: TaskObj):
        try:
            depend = Depends(main_task, dependent_task)
            self.dependencies[depend.id] = depend

        except ValueError as e:
            print(f"[!] Erro ao criar dependência: {e}")
    
    def delete_dependencie(self, main_task: TaskObj, 
                           dependent_task: TaskObj):
        try:
            Depends.remove_dependencie(main_task, dependent_task)

        except ValueError:
            print("[!] Erro ao tentar remover dependência: {e}")

    def get_existent_depends(self, tasks_db_ids: Dict[int, TaskObj]) -> Dict[int, Depends]:
        """
        Args:
           tasks_db_ids (list): Recebe um dicionário com todos os IDs remotos das tasks e o TaskObj respectivo.
        """
        temp_depends: Dict[int, List[int]] = get_all_depends()
        result = {}
        for main_t_ids, dep_t_ids in temp_depends.items():
            if main_t_ids in tasks_db_ids:
                main_task_obj = tasks_db_ids[main_t_ids]
                for dep_task_id in dep_t_ids:
                    if dep_task_id in tasks_db_ids:
                        dep_task_obj = tasks_db_ids[dep_task_id]

                        depend = Depends(main_task_obj, dep_task_obj)
                        result[depend.id] = depend
        return result
