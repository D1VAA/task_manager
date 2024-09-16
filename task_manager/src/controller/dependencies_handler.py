from utils.imports import Dict, Depends, TaskObj, List

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