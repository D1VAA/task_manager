from src.updates_manager import UpdatesHandler
from src.tasks_database.crud_database import (
    create_task,
    create_update,
    delete_task,
    delete_update,
    get_all_updates,
    get_task_id,
    get_tasks_excluding_status,
    update_task,
)
from psycopg2 import OperationalError
from src.utils.colors import Colors
from src.tasks_storage import HandleTasks
from typing import List, Optional, Union
from textwrap import wrap

from src.utils.manage_temp_depend_file import get_all_depends, save_depend_at_temp_file

class Todo(HandleTasks, UpdatesHandler):
    colors_codes = {
        "Done": Colors.GREEN,
        "In Progress": Colors.YELLOW,
        "Not Started": Colors.HARD_RED,
    }

    def __init__(self):
        super().__init__()
        super().__init__()

        # Pega todas as tasks que não possuírem o status como "Done"
        # no banco de dados da Nuvem
        self.tasks = get_tasks_excluding_status("Done")
        tasks_ids = [task.task_id for task in self.tasks.values()]
        self.updates = get_all_updates(tasks_ids)
        self.dependencies = get_all_depends()
        for tid, depends in self.dependencies.items():
            if int(tid) in self.tasks:
                self.tasks[int(tid)].dependencies = depends
        self.__menu()

    def _get_task_db_id(self, task_id: int) -> int:
        """
        Pega o ID da task Local e tenta descobrir o ID da task na Database.
        Caso ela não tenha um, então cria a task na Database e retorna o ID gerado.
        """

        task_db_id = self.tasks[int(task_id)].task_id
        if task_db_id == 0:
            task_id = int(task_id)
            task_name = self.tasks[task_id].name
            task_desc = self.tasks[task_id].description
            task_date = self.tasks[task_id].creation_date
            task_status = self.tasks[task_id].status
            create_task(task_name, task_desc, task_date, task_status)
            task_id_in_db = get_task_id(task_name, task_desc)
            self.tasks[task_id].task_id = task_id_in_db
            return self.tasks[task_id].task_id
        else:
            return task_db_id

    def _show_tasks(self):
        """
        Método utilizado para mostrar as tasks pendentes.
        Não retorna nenhuma valor.
        """

        # Se o dicionário de tasks estiver vazio,
        # significa que não há nenhuma task pendente no banco de dados.
        if not len(self.tasks):
            print(f"{Colors.RED}[!]{Colors.RESET} Nenhuma task pendente.")
            print(
                f"\n{Colors.BLUE}[+] {Colors.RESET}Para criar uma task digite:"
                f"{Colors.BLUE}create{Colors.RESET}")
        else:
            print()
            max_id_len = max([len(str(ids)) for ids in self.tasks.keys()])
            max_tasks_len = max([len(str(tasks.name))
                                for tasks in self.tasks.values()])

            header = (f"| {{:^{max_id_len+2}}} | "
                     f"{{:^{max_tasks_len}}} | {{:^11}} | {{:^7}} | {{:^12}}")
            print(header.format("IDs", "Tasks", "Status", "Updates", "Dependencies"))
            print(header.format("---", "-----", "------", "-------", "------------"))
            print(header.format("", "", "", "", ""))
            for task_id, task_obj in self.tasks.items():
                color_code = self.colors_codes.get(task_obj.status, "")
                task_id_in_db = task_obj.task_id
                if task_id_in_db not in self.updates.keys():
                    updates_count = 0
                else:
                    updates_count = len(self.updates[task_id_in_db])
                depends_count = len(task_obj.dependencies)
                print(
                    header.format(
                        str(task_id),
                        task_obj.name,
                        f"{color_code}{task_obj.status}{Colors.RESET}",
                        updates_count,
                        depends_count,
                    )
                )
            print()

    def _create_task(self, name: Union[List[str], str, None] = None):
        """
        Método para criar uma nova task.
        Não cria diretamente no banco de dados na Nuvem.
        """
        while True:
            name = input("task name> ")
            if not name:
                print(
                    f"{Colors.RED}[!]{
                        Colors.RESET} Nome da task não pode estar vazio!"
                )
            else:
                if isinstance(name, list):
                    name = " ".join(*name)

                description = input("Descriçaõ da Task> ")
                self.new_task(name, description)
                self._show_tasks()
                break

    def _delete_task(
        self, task_id: Union[Optional[str], Optional[int], None] = None
    ) -> None:
        """
        Método para deletar uma task tanto do banco de dados quanto
        na Nuvem quanto no dicionário.
        """
        # Caso o usuário não tenha informado o id na chamada da função.
        if task_id is None:
            task_id = int(input("ID da Task a ser deletada> "))

        if isinstance(task_id, str):
            task_id = int(task_id)

        task = self.tasks[int(task_id)]
        task_db_id = task.task_id

        if task_id not in self.tasks.keys():
            print(f"{Colors.RED}[!]{Colors.RESET} ID não encontrado.")
            return
        try:
            # Pega o id da task no banco de dados se existir.
            delete_task(task_db_id)

            # Delete a task do dicionário de tasks local.
            self.delete_task(task_id)

            print(f"\n{Colors.GREEN}[+]{Colors.RESET} Task deleted.\n")
            self._show_tasks()

        except Exception as e:
            raise Exception(
                f"{Colors.RED}[!]{
                    Colors.RESET}An error occurred while trying to \
                    delete the task: {e}"
            )


    def _edit_task_info(self, task_id: int, info: str) -> str | None:
        """
          Método para atualizar informações de uma task específica.

        Args:
            task_id: ID da task a ser atualizada.
            info: Informação a ser atualizada ('name' ou 'description').
        """

        task_id = int(task_id)
        task_db_id = self.tasks[task_id].task_id

        def change_name():
            new_name = input(f"Novo nome para a task {task_id}> ").strip()

            # Faz a alteração no dicionário.

            self.change_name(task_id, new_name)
            # Faz a alteração no banco de dados da nuvem.
            update_task(name=new_name, task_id=task_db_id)
            self._show_tasks()

        def change_desc():
            self._task_header(task_id)
            new_desc = input("""\r """)

            self.change_description(task_id, new_desc)
            update_task(description=new_desc, task_id=task_db_id)
            print(self.tasks[task_id])

        call_function = {
            ("name", "nome"): change_name,
            ("desc", "description", "descricao", "descrição"): change_desc,
        }
        allowed_options = [opt for tuples in call_function.keys()
                           for opt in tuples]

        def get_dict_key(opt):
            for key, _ in call_function.items():
                if opt in key:
                    return key

        if info not in allowed_options:
            return "Invalid option..."

            # Trecho de código a ser executado caso a opção exista.
        else:
            corresp_key = get_dict_key(info)
            assert corresp_key is not None, "Opt not found."

            call_function[corresp_key]()
            self._show_task_info(task_id)
            
    def _task_header(self, task_id):
        status = self.tasks[task_id].status
        color_code_status = self.colors_codes.get(status, "")
        print()
        print(
            f"{Colors.BLUE}[+]{Colors.RESET} Nome da Task: ",
            self.tasks[task_id].name,
        )
        print(
            f"{Colors.BLUE}[+]{Colors.RESET} Data de criação: ",
            self.tasks[task_id]._creation_date,
        )
        print(
            f"{Colors.BLUE}[+]{Colors.RESET} Status: {
                color_code_status}{status}{Colors.RESET}"
        )
        print(f"\n{'-'*20} Descrição {'-'*20}\n")

    def _handler_show_info(self, *opt):
        if isinstance(opt[0], str) and opt[0] in ['depend', 'dependencie', 'd']:
            self._show_task_relationship(int(opt[1]))
        elif isinstance(opt[0], int) or opt[0].isdigit():
            self._show_task_info(int(opt[0]))
        else:
            print(f"[!] Parâmetro Inválido: {opt[0]}")

    def _show_task_relationship(self, task_id):
        self._task_header(task_id)
        print(self.tasks[int(task_id)].description, end='\n')
        depend_task_ids: List = self.tasks[int(task_id)].dependencies
        depend_task_names = [self.tasks[int(did)].name for did in depend_task_ids]
        print(f'+ Dependencies...', end='\n')
        for did, title in zip(depend_task_ids, depend_task_names):
            print(f'{Colors.PURPLE}[+]{Colors.RESET} {did} {title}')
        print()
    
    def _show_task_info(self, task_id: int):
        """
        Método para mostrar as informações das tasks.
        Infos:
        - Nome
        - Data de criação
        - Status
        - Descrição
        """
        task_id = int(task_id)
        task_id_in_db = self.tasks[task_id].task_id
        self._task_header(task_id)
        wrapped_string = wrap(self.tasks[task_id].description, 100)
        print('\n'.join(wrapped_string))

        # Verifica se essa task possui alguma atualização.
        # Se sim, então irá printar todas as atualizações em ordem decrescente.
        if task_id_in_db in self.updates.keys():
            print(
                f"\n{'-'*20} {Colors.BLUE}Atualizações{Colors.RESET} {'-'*20}"
            )
            for ids, update in reversed(self.updates[task_id_in_db].items()):
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

    def _save_changes_in_db(self):
        """
        Método para salvar as alterações no banco de dados na Nuvem.
        """
        for tid, task in self.tasks.items():
            # O código vai iterar por cada task no dicionário
            # e tentar criar ela dentro do banco de dados.
            if task.task_id == 0:
                self._get_task_db_id(tid)

            else:
            # Caso a task já exista, irá apenas fazer update nas informações,
            # caso elas tenham sido alteradas.
                update_task(status=task.status, 
                            task_id=task.task_id)

        for task_id, updates in self.updates.items():
            for update in updates.values():
                try:
                    create_update(task_id, update.description,
                                  update.creation_date)
                except Exception as e:
                    raise Exception(
                        "An error occurred saving changes "
                    "at the database... ",
                        e,
                    )

    def _manage_task_by_id(self, task_id, *option):
        """
        Método que deve identificar e realizar que tipo de operação o usuário
        está tentando fazer com a task, chamando diretamente pelo número dela.
        """
        option_string = " ".join(option)
        if option_string.lower() in ["done", "in progress", "not started"]:
            new_status = option_string.lower()
            self.update_status(int(task_id), new_status)
            self._show_tasks()

    def _add_update_to_task(self, task_id):
        while True:
            update = input("Escreva> ")
            if not update:
                print(f"{Colors.RED}[!]{
                      Colors.RESET} O texto não pode ser vazio!")
            else:
                task_id_in_db = self._get_task_db_id(int(task_id))
                self.new_update(task_id_in_db, update)
                self._show_tasks()
                break

    def _delete_update(self):
        task_id = int(input("ID da Task> "))
        task_db_id = self.tasks[task_id].task_id
        if task_db_id not in self.updates.keys():
            print(f"{Colors.RED}[!]{Colors.RESET} ID não encontrado.")
            return

        update_local_id = int(input("ID do Update a ser deletado> "))
        try:
            update_obj = self.updates[task_db_id][update_local_id]
            update_id_db = update_obj.update_id_db
            delete_update(update_id_db)
            self.delete_update(
                task_db_id, update_local_id
            )  # Delete do dicionário local.
            self._show_tasks()
        except Exception as e:
            print(e)

    @staticmethod
    def _show_cmds():
        cmds_info = """
        Comandos:
        - create (name [optional])
            Usado para criar uma nova task.
            O parâmetro name (opcional) deve ser uma string de apenas uma palavra.
        - show tasks (no args)
            Usado para mostrar as Tasks ainda pendentes.
        - delete (task_id)
            Usado para deletar uma task. Recebe o ID da task.
        - save (no args)
            Usado para salvar as alterações realizadas.
        - edit (opt)
            Usado para editar o nome ou a descrição das tasks.
            Recebe a informação que vai ser editada (nome ou description).
        - show (task_id)
            Usado para mostrar os detalhes de um task.
            Recebe o ID da task.
        - update (task_id)
            Usado para adicionar uma atualização a uma task.
            Recebe o ID de uma task como parâmetro.
        - delete update (no args)
            Usado para deletar um update de um task.
        - help
            Mostra esse menu.
        - clear
            Limpa o terminal
        - depend
            Cria uma depência entre duas tasks.
        """
        print(cmds_info)

    @staticmethod
    def _clear_terminal():
        from os import system 
        try:
            system('cls') 
        except:
            system('clear')

    def _add_dependencie(self, task_local_id, task_depend_id):
        """
        Método que vai ser chamado no menu para criar dependências entre duas tasks.

        Args:
            task_local_id (int): Recebe o ID da task que vai fazer um vínculo.
            task_depend_id (int): Recebe o ID da task que vai ser vinculada a primeira.
        """
        self.create_dependencie(task_local_id, task_depend_id)
        self._show_tasks()
        depend_ids = self.tasks[int(task_local_id)].dependencies
        print(depend_ids)
        # Função para salvar num arquivo temporário as dependências.
        save_depend_at_temp_file(task_local_id, depend_ids)

    def __menu(self):
        # Chama o método para mostrar os comandos
        self._show_cmds()
        # Chama o método para mostrar as tasks pendentes.
        self._show_tasks()
        available_cmds = {
            "create": self._create_task,
            "show tasks": self._show_tasks,
            "delete": self._delete_task,
            "save": self._save_changes_in_db,
            "edit": self._edit_task_info,
            "show": self._handler_show_info,
            "update": self._add_update_to_task,
            "delete update": self._delete_update,
            "help": self._show_cmds,
            "clear": self._clear_terminal,
            'depend': self._add_dependencie,
        }
        while True:
            try:
                cmd = input("Comando> ").lower().rstrip()
                cmd_len = len(cmd.split())
                if cmd.lower() in ["exit", "quit"]:
                    print(f"\n{Colors.RED}[+]{Colors.RESET} Leaving...")
                    self._save_changes_in_db()
                    break
                if cmd in available_cmds.keys():
                    available_cmds[cmd]()
                elif cmd_len >= 2:
                    cmd, *opt = cmd.split()

                    if cmd.isdigit():
                        self._manage_task_by_id(cmd, *opt)

                    else:
                        available_cmds[cmd](*opt)

            except KeyboardInterrupt:
                self._save_changes_in_db()
                print(f"\n{Colors.RED}[+]{Colors.RESET} Leaving...")
                break
            
            except OperationalError:
                print("[MENU] Erro de operação. Gentileza tentar o comando novamente.") 
            
            except Exception as e:
                print("[MENU] Erro: ", e)

Todo()