from .tasks_handler import TasksHandler
from src.model.updates_strcuture import Update
from src.utils.colors import Colors
from src.tasks_database import crud_database as task_db_h
from textwrap import wrap
from src.utils.imports import Dict
from os import system
import platform
from prompt_toolkit import PromptSession
from prompt_toolkit.history import InMemoryHistory

colors_codes = {
    "Done": Colors.GREEN,
    "In Progress": Colors.YELLOW,
    "Not Started": Colors.HARD_RED,
}

th = TasksHandler()
history = InMemoryHistory()
s = PromptSession(history=history)


def get_input(msg, empty=False):
    while True:
        user_input = s.prompt(f"{msg}> ").rstrip()
        if user_input == "" and empty:
            return ""
        else:
            return user_input


class ClearScreen:
    @classmethod
    def execute(cls):
        try:
            if platform.system() == "Windows":
                system("cls")
            else:
                system("clear")
        except Exception as e:
            print(f"Erro ao tentar limpar a tela: {e}")


class CreateTask:
    @classmethod
    def execute(cls):
        name = get_input("Nome da task")
        desc = get_input("Descrição da task")
        th.new_task(name, desc)
        ShowInfo._show_all_tasks()


class Delete:
    @classmethod
    def _delete_task(cls, t_local_id: str | int | None = None):
        if t_local_id is None:
            t_local_id = int(get_input("ID da task a ser deletada"))

        if isinstance(t_local_id, str) and t_local_id.isdigit():
            t_local_id = int(t_local_id)

        try:
            th.delete_task(t_local_id)
            task_db_id = th.get_specific_db_id(t_local_id)
            task_db_h.delete_task(task_db_id)
            print("\n+ Task deletada!\n")
        except:
            pass

    @classmethod
    def _delete_update(
        cls, task_id: int | str | None = None, update_id: int | str | None = None
    ):
        if task_id is None:
            task_id = int(s.prompt("ID da Task> "))
        elif isinstance(task_id, str) and task_id.isdigit():
            task_id = int(task_id)

        if task_id not in th.tasks.keys():
            print(f"{Colors.RED}[!]{Colors.RESET}Task com ID {
                  task_id} não encontrado.")
            return

        if update_id is None:
            update_id = int(s.prompt("ID do Update a ser deletado> "))
        elif isinstance(update_id, str) and update_id.isdigit():
            update_id = int(update_id)

        if update_id not in th.tasks[task_id].updates.keys():
            print(f"{Colors.RED}[!]{Colors.RESET}Task com ID {
                  task_id} não encontrado.")

        update_obj = th.get_update_obj(task_id, update_id)
        # Tenta deletar o update na database, caso ele exista.
        try:
            update_id_db = task_db_h.get_update_id(update_obj.description)
            if update_id_db is not None:
                task_db_h.delete_update(update_id_db)
        except:...

        th.delete_update(task_id, update_id)
        ShowInfo._show_all_tasks()

    @classmethod
    def _del_dependencie(cls):
        task_id = int(s.prompt("Main task ID: "))
        dependent_task_id = int(s.prompt("Dependent task ID: "))
        th.delete_dependencie(task_id, dependent_task_id)
        try:
            main_obj = th.tasks[task_id]
            depend_obj = th.tasks[dependent_task_id]
            task_db_h.delete_dependencie(main_obj.task_id, depend_obj.task_id)
        except:
            ...
        ShowInfo._show_all_tasks()

    @classmethod
    def execute(cls, *opt):
        if opt[0] in ["depend", "d", "dependencie"]:
            cls._del_dependencie()
        elif opt[0] in ["update"]:
            cls._delete_update(*opt[1:])
        elif opt[0].isdigit() or isinstance(opt[0], int):
            cls._delete_task(opt[0])


class EditTask:
    @classmethod
    def execute(cls, task_id: str | int | None = None, info: str | None = None):
        info_opts = {
            "name": cls._change_name,
            "nome": cls._change_name,
            "desc": cls._change_description,
            "description": cls._change_description,
            "descricao": cls._change_description,
            "descrição": cls._change_description,
        }
        if isinstance(task_id, str):
            task_id = int(task_id)
        if task_id is None:
            task_id = int(get_input("ID da task a ser editada"))
        if info is None:
            info = get_input("Informação a ser editada [name/desc]")
        try:
            info_opts[info](task_id)
        except Exception as e:
            print("[!] Comando não encontrado... Erro: ", e)

    @staticmethod
    def _change_name(task_id: int):
        try:
            new_name = get_input("Novo nome para a Task")
            th.change_name(task_id, new_name)
            task_db_id = th.get_specific_db_id(task_id)
            task_db_h.update_task(name=new_name, task_id=task_db_id)
        except:
            ...

    @staticmethod
    def _change_description(task_id: int):
        try:
            ShowInfo._task_header(th.tasks[task_id])
            print(f"{Colors.RED}Escreva...{Colors.RESET}")
            new_desc = s.prompt("""\r""")
            th.change_description(task_id, new_desc)
            task_db_id = th.get_specific_db_id(task_id)
            task_db_h.update_task(description=new_desc, task_id=task_db_id)

        except:
            ...


class ShowInfo:
    @staticmethod
    def _task_header(task_obj):
        status = task_obj.status
        color_code_status = colors_codes.get(status, "")
        print()
        print(
            f"[{Colors.BLUE}+{Colors.RESET}] Nome da Task: ",
            task_obj.name,
        )
        print(
            f"[{Colors.BLUE}+{Colors.RESET}] Data de criação: ",
            task_obj._creation_date,
        )
        print(
            f"[{Colors.BLUE}+{Colors.RESET}] Status: {
                color_code_status}{status}{Colors.RESET}"
        )
        print(f"\n{'-'*20} Descrição {'-'*20}\n")

    @staticmethod
    def _show_all_tasks():
        tasks = th.tasks
        if not len(th.tasks):
            print(f"{Colors.RED}[!]{Colors.RESET} Nenhuma task pendente.")
            print(
                f"\n{Colors.BLUE}[+] {Colors.RESET}Para criar uma task digite:"
                f"{Colors.BLUE}create{Colors.RESET}",
                end="\n",
            )
        else:
            print()
            max_id_len = max([len(str(ids)) for ids in tasks.keys()])
            max_tasks_len = max([len(str(tasks.name))
                                for tasks in tasks.values()])

            header = (
                f"| {{:^{max_id_len+2}}} | "
                f"{{:^{max_tasks_len}}} | {{:^11}} | {{:^7}} | {{:^12}}"
            )
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
                        f"{color_code}{task_obj.status:^11}{Colors.RESET}",
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
        print("\n".join(wrapped_string))

        # Verifica se essa task possui alguma atualização.
        # Se sim, então irá printar todas as atualizações em ordem decrescente.
        if len(updates):
            print(f"\n{'-'*20} {Colors.BLUE}Atualizações{Colors.RESET} {'-'*20}")
            for ids, update in reversed(updates.items()):
                print(
                    f"[{Colors.BLUE}+{Colors.RESET}] Número: {
                        Colors.BLUE}{ids}{Colors.RESET}",
                    end=" | ",
                )
                print(
                    f"[{Colors.BLUE}+{Colors.RESET}] Data de criação: ",
                    update.creation_date,
                )
                wrapped_string = wrap(update.description, 80)
                print(f'{"-"*60}')
                print()
                print("\n".join(wrapped_string))
                print(f"\n{'-'*25}+\n")
        print()

    @classmethod
    def _show_task_dependencies(cls, task_obj):
        cls._task_header(task_obj)
        print(task_obj.description, end="\n")
        depend_task_dict = task_obj.dependencies
        # depend_task_dict: dict = {lid: obj.name for lid, obj in enumerate(task_obj.dependencies)}

        print(f"\n[{Colors.YELLOW}+{Colors.RESET}] Dependencies:", end="\n")
        print(f'{"-"*20}')
        for task_id, task_obj in depend_task_dict.items():
            print(f"|{Colors.PURPLE} {task_id} {
                  Colors.RESET}| => {task_obj.name}")
        print()

    @classmethod
    def execute(cls, *opt: str):
        tasks = th.tasks
        if isinstance(opt[0], str) and opt[0] in [
            "depend",
            "dependencie",
            "d",
            "depends",
            "dependencies",
        ]:
            task_obj = tasks[int(opt[1])]
            cls._show_task_dependencies(task_obj)
        elif isinstance(opt[0], int) or opt[0].isdigit():
            task_obj = tasks[int(opt[0])]
            cls._show_specific_task_info(task_obj)
        else:
            cls._show_all_tasks()


class SaveChanges:
    @classmethod
    def execute(cls):
        tasks = th.tasks
        for tid, task_obj in tasks.items():
            if task_obj.id == 0:
                msg = task_db_h.create_task(
                    task_obj.name,
                    task_obj.description,
                    task_obj.creation_date,
                    task_obj.status,
                )
                assert isinstance(msg, dict)
                th.tasks[tid].id = msg["task_id"]

            else:
                updates = {
                    u.description: u.creation_date for u in task_obj.updates.values()
                }
                dependencies = [d.id for d in task_obj.dependencies.values()]
                task_db_h.update_task(
                    name=task_obj.name,
                    description=task_obj.description,
                    status=task_obj.status,
                    task_id=task_obj.id,
                    updates=updates,
                    dependencies=dependencies,
                )
                try:
                    for task_id in th._deleted_tasks:
                        task_db_h.delete_task(task_id)
                except:
                    ...


class ChangeTaskStatus:
    @classmethod
    def execute(cls, task_id, *option):
        option_string = " ".join(option)
        if option_string.lower() in ["done", "in progress", "not started"]:
            new_status = option_string.lower()
            msg = th.update_status(int(task_id), new_status)
            if msg is not None:
                print(f'[{Colors.BLUE}+{Colors.RESET}]{msg}')
            else:
                ShowInfo._show_all_tasks()


class AddUpdate:
    @classmethod
    def execute(cls, task_id):
        while True:
            update = s.prompt("Escreva> ")
            if not update:
                print(f"{Colors.RED}[!]{
                    Colors.RESET} O texto não pode ser vazio!")
            else:
                th.create_update(task_id, update)
                ShowInfo._show_all_tasks()
                break


class AddDependencie:
    @classmethod
    def execute(
        cls, task_id: str | int | None = None, t_depend_id: str | int | None = None
    ):
        if task_id is None:
            task_id = int(s.prompt("ID da Task que vai receber a dependência > "))
        elif isinstance(task_id, str) and task_id.isdigit():
            task_id = int(task_id)
        if t_depend_id is None:
            t_depend_id = int(s.prompt("ID da task dependente > "))
        elif isinstance(t_depend_id, str) and t_depend_id.isdigit():
            t_depend_id = int(t_depend_id)

        th.create_dependencie(task_id, t_depend_id)
        ShowInfo._show_all_tasks()
