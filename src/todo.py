from utils.colors import Colors
from tasks_storage import HandleTasks

class Todo(HandleTasks):
    def __init__(self):
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
        print(f"\n{'-'*20} Descrição {'-'*20}\n", self.tasks[task_id].description)
        print()
    
    def __menu(self):
        self._show_tasks()
        while True:
            try:
                opt = input('Comando> ').lower()
                opt_len = len(opt.split())
                if opt == 'create':
                    self._create_task()
                
                elif opt_len <= 2:
                    if 'delete' in opt:
                        task_id = opt.split()[-1]
                        del self.tasks[task_id]
                    elif opt.isdigit():
                        self._show_task_info(int(opt))

                elif opt_len > 2:
                    try:
                        task_id, *new_status = opt.split()
                        new_status = " ".join(new_status)
                        if task_id.isdigit():
                            self.tasks[int(task_id)].status = new_status
                            self._show_tasks()
                    except Exception as e:
                        print(e)
                else:
                    print("[!] Quantidade de argumento inválida.\nPara alterar o status de uma task digite o ID e o novo status da task ao lado.")

            except KeyboardInterrupt:
                print('\n[+] Leaving...')
                break
