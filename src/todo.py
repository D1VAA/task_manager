from tasks_database.crud_database import create_task, delete_task, get_task_id, get_tasks_excluding_status, update_task
from utils.colors import Colors
from tasks_database.tasks_storage import HandleTasks

class Todo(HandleTasks):
    def __init__(self):
        self.tasks = get_tasks_excluding_status('Done')
        super().__init__()
        self.__menu()
    
    def _show_tasks(self):
        if not len(self.tasks):
            print(f'{Colors.RED}[!]{Colors.RESET} Você ainda não criou nenhuma task.')
            print(f'\n{Colors.BLUE}[+] {Colors.RESET}Para criar uma task digite: {Colors.BLUE}create{Colors.RESET}')
        else:
            print()
            max_id_len = max([len(str(ids)) for ids in self.tasks.keys()])
            max_tasks_len = max([len(str(tasks.name)) for tasks in self.tasks.values()])
            max_status_len = max([len(str(tasks.status)) for tasks in self.tasks.values()])
            header = f'| {{:^{max_id_len+2}}} | {{:^{max_tasks_len}}} | {{:^{max_status_len}}}'
            print(header.format("IDs", "Tasks", "Status"))
            print(header.format("---", "-----", "------"))
            print(header.format("", "", ""))
            for task_id, task_obj in self.tasks.items():
                print(header.format(str(task_id), task_obj.name, task_obj.status)) 
            print()

    def _create_task(self):
        while True:
            name = input('Nome da Task> ')
            if name == '':
                print(f'{Colors.RED}[!]{Colors.RESET} Nome inválido!')
            else:
                description = input("Descriçaõ da Task> ")
                self.new_task(name, description)
                self._show_tasks()
                break
        
    def _show_task_info(self, task_id):
        print()
        print(f"{Colors.BLUE}[+]{Colors.RESET} Nome da Task: ",self.tasks[task_id].name)
        print(f"{Colors.BLUE}[+]{Colors.RESET} Data de criação: ", self.tasks[task_id]._creation_date)
        print(f"{Colors.BLUE}[+]{Colors.RESET} Status: ", self.tasks[task_id].status)
        print(f"\n{'-'*20} Descrição {'-'*20}\n\n", self.tasks[task_id].description)
        print()
    
    def _save_tasks_in_db(self):
        for task in self.tasks.values():
            try:
                create_task(task.name, task.description, task.creation_date, task.status)
            except ValueError:
                update_task(task.name, task.description, task.status)
    
    def __menu(self):
        self._show_tasks()
        while True:
            try:
                opt = input('Comando> ').lower()
                opt_len = len(opt.split())
                if opt == 'create':
                    self._create_task()

                elif opt == 'show tasks':
                    self._show_tasks()
                
                elif opt_len >= 2:
                    if opt.split()[0].isdigit():
                        task_id, *new_status = opt.split()
                        new_status = " ".join(new_status).lower()
                        self.update_status(int(task_id), new_status)
                        self._show_tasks()
                    elif 'delete' in opt and opt.split()[-1].isdigit():
                        task_id = opt.split()[-1]
                        task = self.tasks[int(task_id)]
                        try:
                            task_db_id = get_task_id(task.name)
                            delete_task(task_db_id)
                        except Exception as e:
                            pass
                        del self.tasks[int(task_id)]
                    elif opt.isdigit():
                        self._show_task_info(int(opt))

                elif opt_len > 2:
                    try:
                        task_id, *new_status = opt.split()
                        new_status = " ".join(new_status).lower()
                        if task_id.isdigit():
                            self.update_status(int(task_id), new_status)
                            self._show_tasks()
                    except Exception as e:
                        print(e)
                else:
                    print("[!] Quantidade de argumento inválida.\nPara alterar o status de uma task digite o ID e o novo status da task ao lado.")

            except KeyboardInterrupt:
                self._save_tasks_in_db()
                print('\n[+] Leaving...')
                break
