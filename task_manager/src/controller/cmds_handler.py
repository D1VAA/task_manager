from tasks_handler import TasksHandler
from model.updates_strcuture import Update
from utils.colors import Colors
from tasks_database import crud_database as task_db_h
from textwrap import wrap
from typing import Dict, List, Any

th = TasksHandler()
colors_codes = {
    "Done": Colors.GREEN,
    "In Progress": Colors.YELLOW,
    "Not Started": Colors.HARD_RED,
}

def get_input(msg, empty=False):
    while True:
        user_input = input(f'{Colors.RED}[+]{Colors.RESET} {msg}> ').lower().rstrip()
        if user_input == '' and empty:
            return ''
        else:
            return user_input

class CreateTask:
    @classmethod
    def execute(cls):
        name = get_input('Nome da task')
        desc = get_input('Descrição da task')
        th.new_task(name, desc)
         
class DeleteTask:
    """
    Comando que irá deletar a task tanto localmente quanto no banco de dados.
    """
    @classmethod
    def execute(cls, t_local_id: str|int|None = None):
        if t_local_id is None:
            t_local_id = int(get_input('ID da task a ser deletada'))

        if isinstance(t_local_id, str):
            taks_id = int(t_local_id)

        th.delete_task(t_local_id)
        task_db_id = th.get_specific_db_id(t_local_id)
        task_db_h.delete_task(task_db_id)

class EditTask:
    @classmethod
    def execute(cls, task_id: str|int|None=None, info: str|None=None):
        info_opts = {
            'name': cls.change_name,
            'nome': cls.change_name,
            'desc': cls.change_description,
            'description': cls.change_description,
            'descricao': cls.change_description,
            'descrição': cls.change_description,
        }
        if isinstance(task_id, str):
            task_id = int(task_id) 
        if task_id is None:
            task_id = int(get_input('ID da task a ser editada'))
        if info is None:
            info = get_input('Informação a ser editada [name/desc]')
        try:
            info_opts[info](task_id)
        except Exception as e:
            print("[!] Comando não encontrado... Erro: ", e)
        
    @staticmethod
    def change_name(task_id: int):
        new_name = get_input('Novo nome para a Task')
        th.change_name(task_id, new_name)
        task_db_id = th.get_specific_db_id(task_id)
        task_db_h.update_task(name=new_name, task_id=task_db_id)
    
    @staticmethod
    def change_description(task_id: int):
        new_desc = input("""\r""")
        th.change_description(task_id, new_desc)
        task_db_id = th.get_specific_db_id(task_id)
        task_db_h.update_task(description=new_desc, task_id=task_db_id)
        
class ShowInfo:
    @staticmethod
    def _task_header(task_obj):
        status = task_obj.status
        color_code_status = colors_codes.get(status, "")
        print()
        print(
            f"{Colors.BLUE}[+]{Colors.RESET} Nome da Task: ",
            task_obj.name,
        )
        print(
            f"{Colors.BLUE}[+]{Colors.RESET} Data de criação: ",
            task_obj._creation_date,
        )
        print(
            f"{Colors.BLUE}[+]{Colors.RESET} Status: {
                color_code_status}{status}{Colors.RESET}"
        )
        print(f"\n{'-'*20} Descrição {'-'*20}\n")

    @staticmethod
    def _show_all_tasks(tasks):
        if not len(th.tasks):
            print(f"{Colors.RED}[!]{Colors.RESET} Nenhuma task pendente.")
            print(
                f"\n{Colors.BLUE}[+] {Colors.RESET}Para criar uma task digite:"
                f"{Colors.BLUE}create{Colors.RESET}")
        else:
            print()
            max_id_len = max([len(str(ids)) for ids in tasks.keys()])
            max_tasks_len = max([len(str(tasks.name))
                                for tasks in tasks.values()])

            header = (f"| {{:^{max_id_len+2}}} | "
                     f"{{:^{max_tasks_len}}} | {{:^11}} | {{:^7}} | {{:^12}}")
            print(header.format("IDs", "Tasks", "Status", "Updates", "Dependencies"))
            print(header.format("---", "-----", "------", "-------", "------------"))
            print(header.format("", "", "", "", ""))
            for task_l_id, task_obj in tasks.items():
                color_code = colors_codes.get(task_obj.status, "")
                updates_count = len(tasks[task_l_id].updates)
                depends_count = len(task_obj.dependencies)
                print(
                    header.format(
                        str(task_l_id),
                        task_obj.name,
                        f"{color_code}{task_obj.status}{Colors.RESET}",
                        updates_count,
                        depends_count,
                    )
                )
            print()

    @classmethod
    def _show_specific_task_info(cls, task_obj):
        updates: Dict[int, Update] = task_obj.updates
        wrapped_string = wrap(task_obj.description, 100)
        cls._task_header(task_obj)
        print('\n'.join(wrapped_string))

        # Verifica se essa task possui alguma atualização.
        # Se sim, então irá printar todas as atualizações em ordem decrescente.
        if len(updates):
            print(
                f"\n{'-'*20} {Colors.BLUE}Atualizações{Colors.RESET} {'-'*20}"
            )
            for ids, update in reversed(updates.items()):
                print(
                    f"{Colors.BLUE}[+]{Colors.RESET} Número: {
                        Colors.BLUE}{ids}{Colors.RESET}"
                , end=' | ')
                print(
                    f"{Colors.BLUE}[+]{Colors.RESET} Data de criação: ",
                    update.creation_date,
                )
                wrapped_string = wrap(update.description, 80)
                print('\n'.join(wrapped_string))
                print(f"\n{'-'*25}+\n")
        print()

    @classmethod
    def _show_task_dependencies(cls, task_obj):
        cls._task_header(task_obj)
        print(task_obj.description, end='\n')
        depend_task_dict: dict = {lid: obj.name for lid, obj in enumerate(task_obj.dependencies)}

        print(f'+ Dependencies...', end='\n')
        for local_id, title in depend_task_dict.items():
            print(f'{Colors.PURPLE}[+]{Colors.RESET} {local_id} {title}')
        print()
    
    @classmethod
    def execute(cls, *opt: str):
        tasks = th.tasks
        if isinstance(opt[0], str) and opt[0] in ['depend', 'dependencie', 'd']:
            task_obj = tasks[int(opt[1])]
            cls._show_task_dependencies(task_obj)
        elif isinstance(opt[0], int) or opt[0].isdigit():
            task_obj = tasks[int(opt[0])]
            cls._show_specific_task_info(task_obj)
        else:
            cls._show_all_tasks(tasks)

class SaveChanges:
    @classmethod
    def execute(cls):
        tasks = th.tasks
        for tid, task_obj in tasks.items():
            if task_obj.task_id == 0:
                task_db_h.create_task(task_obj.name, 
                                      task_obj.description, 
                                      task_obj.creation_date,
                                      task_obj.status)

            else:
                task_db_h.update_task(status=task_obj.status, 
                            task_id=task_obj.task_id)
