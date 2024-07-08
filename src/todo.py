from tasks_database.crud_database import create_task, delete_task, get_task_id, get_tasks_excluding_status, update_task
from utils.colors import Colors
from tasks_database.tasks_storage import HandleTasks
from typing import List, Optional, Union
from logger import logger

class Todo(HandleTasks):
    def __init__(self):
        # Pega todas as tasks que não possuírem o status como "Done" no banco de dados da Nuvem
        logger.debug("Iniciando o gerenciador de tasks.")
        self.tasks = get_tasks_excluding_status('Done') 
        super().__init__()
        self.__menu()
    
    def _show_tasks(self):
        """
        Método utilizado para mostrar as tasks pendentes.

        Não retorna nenhuma valor.
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

    def _create_task(self, name: Union[List, str]=None):
        """
        Método para criar uma nova task. Não cria diretamente no banco de dados na Nuvem.
        """
        while True:
            if isinstance(name, list):
                name = ' '.join(name)

            if name is None:
                name = input('Nome da Task> ')

            if not name: 
                print(f'{Colors.RED}[!]{Colors.RESET} Nome da task não pode estar vazio!')
            else:
                description = input("Descriçaõ da Task> ")
                logger.info(f'Criando nova task no dicionário: {name}')
                self.new_task(name, description)
                self._show_tasks()
                break
    
    def _delete_task(self, task_id: Union[Optional[str], Optional[int]] = None) -> None:
        """
        Método para deletar uma task tanto do banco de dados na Nuvem quanto no dicionário.
        """
        task_id = int(task_id)
        if task_id not in self.tasks.keys():
            print(f'{Colors.RED}[!]{Colors.RESET} ID não encontrado.')
            return

        try:
            # Caso o usuário não tenha informado o id na chamada da função.
            if task_id is None:
                task_id = int(input('ID da Task a ser deletada> '))
            task = self.tasks[int(task_id)]
            try:
                # Pega o id da task no banco de dados se existir.
                task_db_id = get_task_id(task.name)
                logger.info(f'Deletou do banco de dados a task de ID: {task_db_id} - NOME: {task.name}')
                delete_task(task_db_id)
            except:...

            # Delete a task do dicionário de tasks local.
            self.delete_task(task_id)
            logger.info(f'Deletou do dicionário a task de nome: {task.name}')

            print(f"\n{Colors.GREEN}[+]{Colors.RESET} Task deleted.\n")
            self._show_tasks()

        except Exception as e:
            logger.info(f'Falha ao deletar a task de nome: {task.name}')
            print(f"{Colors.RED}[!]{Colors.RESET}An error occurred while trying to delete the task: {e}")

    def _update_task_info(self, task_id:int, info: str) -> None:
        """
          Método para atualizar informações de uma task específica.

        Args:
            task_id: ID da task a ser atualizada.
            info: Informação a ser atualizada ('name' ou 'description').
        """
        if info.lower() in ['name', 'nome']: 
            old_name = self.tasks[int(task_id)].name
            new_name = input(f"Novo nome para a task {task_id}> ").strip()

            # Faz a alteração no dicionário.
            self.change_name(task_id, new_name)
            logger.info(f"Editou uma task no dicionário. Nome: {old_name} > {new_name}")

            try:
                # Pega o ID da task no banco de dados.
                task_id_db = get_task_id(self.tasks[int(task_id)].name)
                # Faz a alteração no banco de dados na nuvem.
                update_task(name=new_name, task_id=task_id_db)
                logger.info(f"Editou uma task no banco de dados. Nome - {old_name} > {new_name}")
            except Exception as e:
                logger.info(f'Falhou ao tentar editar o nome de uma task no banco de dados. Erro: {e}')

            self._show_tasks()

        elif info.lower() in ['description', 'descrição', 'descricao', 'desc']:
            colors_codes = {
                "Done": Colors.GREEN,
                "In Progress": Colors.YELLOW,
                "Not Started": Colors.HARD_RED
            }
            task_id = int(task_id)
            status = self.tasks[task_id].status
            color_code_status = colors_codes.get(status, "")
            print()
            print(f"{Colors.BLUE}[+]{Colors.RESET} Nome da Task: ",self.tasks[task_id].name)
            print(f"{Colors.BLUE}[+]{Colors.RESET} Data de criação: ", self.tasks[task_id]._creation_date)
            print(f"{Colors.BLUE}[+]{Colors.RESET} Status: {color_code_status}{status}{Colors.RESET}")
            print(f"\n{'-'*20} Descrição {'-'*20}\n")

            old_desc = self.tasks[task_id].description
            new_desc = input(f"\r ")
            
            # Faz a alteração no dicionário.
            self.change_description(task_id, new_desc)
            logger.info(f"Editou uma task no dicionário. Descrição - {old_desc} > {new_desc}")

            #Faz a alteração no banco de dados na nuvem.
            try:
                # Pega o ID da task no banco de dados.
                task_id_db = get_task_id(self.tasks[task_id].name)
                update_task(description=new_desc, task_id=task_id_db)
                logger.info(f"Editou uma task no banco de dados. Descrição - {old_desc} > {new_desc}")

            except Exception as e:
                logger.info(f'Falhou ao tentar editar a descrição de uma task no banco de dados. Erro: {e}')
                print(e)

            self._show_task_info(task_id)

        else:
            raise ValueError('Option not found.')

    def _show_task_info(self, task_id: int):
        """
        Método para mostrar as informações das tasks.
        Infos:
        - Nome
        - Data de criaçã
        - Status
        - Descrição
        """
        task_id = int(task_id)
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
                logger.info(f'Criou uma no banco de dados. Nome: {task.name}')
            # Caso a task já exista, irá apenas fazer update nas informações, caso elas tenham sido alteradas.
            except ValueError:
                task_db_id = get_task_id(task.name)
                update_task(task.name, task.description, task.status, task_id=task_db_id)
                #logger.info(f'Editou uma task no banco de dados. ID: {task_db_id}')
    
    def _manage_task_by_id(self, task_id, *option):
        """
        Método que deve identificar e realizar que tipo de operação o usuário está tentando fazer com a task, chamando diretamente pelo número dela.
        """
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
                          'delete': self._delete_task,
                          'save': self._save_tasks_in_db,
                          'update': self._update_task_info,
                          'show': self._show_task_info}
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

            except KeyboardInterrupt:
                self._save_tasks_in_db()
                print(f'\n{Colors.RED}[+]{Colors.RESET} Leaving...')
                break

            except:
                pass
