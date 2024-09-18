from psycopg2 import OperationalError
from .cmds_handler import *

available_cmds = {
    'create': CreateTask.execute,
    'delete': DeleteTask.execute,
    'show': ShowInfo.execute,
    'save': SaveChanges.execute,
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
                    #self._save_changes_in_db()
                    break
                if cmd in available_cmds.keys():
                    available_cmds[cmd]()
                elif cmd_len >= 2:
                    cmd, *opt = cmd.split()

                    if cmd.isdigit():...
                        #self._manage_task_by_id(cmd, *opt)

                    else:...
                        #available_cmds[cmd](*opt)

            except KeyboardInterrupt:
                #self._save_changes_in_db()
                print(f"\n{Colors.RED}[+]{Colors.RESET} Leaving...")
                break
            
            except OperationalError:
                print("[MENU] Erro de operação. Gentileza tentar o comando novamente.") 
            
            except Exception as e:
                print("[MENU] Erro: ", e)