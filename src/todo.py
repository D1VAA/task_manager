from tasks_database.crud_database import create_task, delete_task, get_task_id, get_tasks_excluding_status, update_task
from utils.colors import Colors
from tasks_database.tasks_storage import HandleTasks
from typing import Optional

class Todo(HandleTasks):
    def __init__(self):
        # Pega todas as tasks que não possuírem o status como "Done" no banco de dados da Nuvem
        self.tasks = get_tasks_excluding_status('Done') 
        super().__init__()
        self.__menu()
    
    def _show_tasks(self):
        """
        Método utilizado para mostrar as tasks pendentes.
        """
        # Se o dicionário de tasks estiver vazio, significa que não há nenhuma task pendente no banco de dados.
        if not len(self.tasks):
            print(f'{Colors.RED}[!]{Colors.RESET} Nenhuma task pendente.')
            print(f'\n{Colors.BLUE}[+] {Colors.RESET}Para criar uma task digite: {Colors.BLUE}create{Colors.RESET}')
        else:
            print()
            max_id_len = max([len(str(ids)) for ids in self.tasks.keys()])
            max_tasks_len = max([len(str(tasks.name)) for tasks in self.tasks.values()])
            max_status_len = max([len(str(tasks.status)) for tasks in self.tasks.values()])

            colors_codes = {
                "Done": Colors.GREEN,
                "In Progress": Colors.YELLOW,
                "Not Started": Colors.HARD_RED
            }
            
            header = f'| {{:^{max_id_len+2}}} | {{:^{max_tasks_len}}} | {{:^{max_status_len}}}'
            print(header.format("IDs", "Tasks", "Status"))
            print(header.format("---", "-----", "------"))
            print(header.format("", "", ""))
            for task_id, task_obj in self.tasks.items():
                color_code = colors_codes.get(task_obj.status, "")
                print(header.format(str(task_id), task_obj.name, f"{color_code}{task_obj.status}{Colors.RESET}")) 
            print()

    def _create_task(self):
        """
        Método para criar uma nova task. Não cria diretamente no banco de dados na Nuvem.
        """
        while True:
            name = input('Nome da Task> ')
            if name == '':
                print(f'{Colors.RED}[!]{Colors.RESET} Nome inválido!')
            else:
                description = input("Descriçaõ da Task> ")
                self.new_task(name, description)
                self._show_tasks()
                break
    
    def _delete_task(self, task_id: Optional[int] = None) -> None:
        """
        Método para deletar uma task tanto do banco de dados na Nuvem quanto no dicionário.
        """
        if task_id is None:
            task_id = int(input('ID da Task a ser deletada> '))
        task = self.tasks[int(task_id)]
        try:
            task_db_id = get_task_id(task.name)
            delete_task(task_db_id)
        except Exception:pass
        del self.tasks[int(task_id)]

        
    def _show_task_info(self, task_id):
        """
        Método para mostrar as informações das tasks.
        Infos:
        - Nome
        - Data de criaçã
        - Status
        - Descrição
        """
        colors_codes = {
            "Done": Colors.GREEN,
            "In Progress": Colors.YELLOW,
            "Not Started": Colors.HARD_RED
        }
        status = self.tasks[task_id].status
        color_code_status = colors_codes.get(status, "")
        print()
        print(f"{Colors.BLUE}[+]{Colors.RESET} Nome da Task: ",self.tasks[task_id].name)
        print(f"{Colors.BLUE}[+]{Colors.RESET} Data de criação: ", self.tasks[task_id]._creation_date)
        print(f"{Colors.BLUE}[+]{Colors.RESET} Status: {color_code_status}{status}{Colors.RESET}")
        print(f"\n{'-'*20} Descrição {'-'*20}\n\n", self.tasks[task_id].description)
        print()
    
    def _save_tasks_in_db(self):
        """
        Método para salvar as alterações no banco de dados na Nuvem.
        """
        for task in self.tasks.values():
            # O código vai iterar por cada task no dicionário e tentar criar ela dentro do banco de dados.
            try:
                create_task(task.name, task.description, task.creation_date, task.status)
            # Caso a task já exista, irá apenas fazer update nas informações, caso elas tenham sido alteradas.
            except ValueError:
                update_task(task.name, task.description, task.status)
    
    def _manage_task_by_id(self, task_id, *option):
        option_string = " ".join(option)
        if option_string.lower() in ['done', 'in progress', 'not started']:
            new_status = option_string.lower()
            self.update_status(int(task_id), new_status)
            self._show_tasks()
    
    def __menu(self):
        # Chama o método para mostrar as tasks pendentes.
        self._show_tasks()
        available_cmds = {'create': self._create_task, 
                          'show tasks': self._show_tasks,
                          'delete': self._delete_task}
        while True:
            try:
                cmd = input('Comando> ').lower().rstrip()
                cmd_len = len(cmd.split())
                if cmd in available_cmds:
                    available_cmds[cmd]()
                elif cmd_len >= 2:
                    cmd, *opt = cmd.split()
                    if cmd.isdigit():
                        self._manage_task_by_id(cmd, *opt)
                    else:
                        available_cmds[cmd](*opt)

                elif cmd_len == 1 and cmd.isdigit():
                    self._show_task_info(int(cmd))

            except KeyboardInterrupt:
                self._save_tasks_in_db()
                print(f'\n{Colors.RED}[+]{Colors.RESET} Leaving...')
                break

            except:
                pass
