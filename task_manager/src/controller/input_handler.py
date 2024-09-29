from psycopg2 import OperationalError
from .cmds_handler import *

available_cmds = {
    'create': CreateTask.execute,
    'delete': Delete.execute,
    'show': ShowInfo.execute,
    'save': SaveChanges.execute,
    'edit': EditTask.execute,
    'update': AddUpdate.execute,
    'depend': AddDependencie.execute,
    'clear': ClearScreen.execute,
}


class InputHandler:
    def cmd_input(self):
        ShowInfo._show_all_tasks()        
        while True:
            try:
                cmd = input("Comando> ").lower().rstrip()
                cmd_len = len(cmd.split())
                if cmd.lower() in ["exit", "quit"]:
                    print(f"\n{Colors.RED}[+]{Colors.RESET} Leaving...")
                    SaveChanges.execute()
                    break
                if cmd in available_cmds.keys():
                    available_cmds[cmd]()
                elif cmd_len >= 2:
                    cmd, *opt = cmd.split()

                    if cmd.isdigit():
                        ChangeTaskStatus.execute(cmd, *opt)

                    else:
                        available_cmds[cmd](*opt)

            except KeyboardInterrupt:
                try:
                    SaveChanges.execute()
                except:...
                print(f"\n{Colors.RED}[+]{Colors.RESET} Leaving...")
                break
            
            except OperationalError:
                print("[MENU] Erro de operação. Gentileza tentar o comando novamente.") 
            
            except Exception as e:
                print("[MENU] Erro: ", e)
