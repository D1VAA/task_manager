from utils.colors import Colors
from database.crud_database import create_freight, query_freight
from pathlib import Path
import send2trash

title: str = '''
TITLE EXAMPLE
'''

def get_input(msg):
    obj = input(f'{Colors.PURPLE}[-]{Colors.RESET} {msg}').lower().rstrip()
    return obj 

class Menu:
    def __init__(self):
        self._initial_panel()
    
    def _initial_panel(self):
        data = f'''
        \r-------------------------------------------------------------
        \r\t{Colors.RED}[1] {Colors.YELLOW}Add a new freight to database from file.
        \r\t{Colors.RED}[2] {Colors.YELLOW}Query an existing freight at database.
          {Colors.RESET}
        '''
        print(data)
        opts = {1: self._add_freight, 2: self._query_freight}
        try:
            while True:
                opt = int(input(f'Choose an option{Colors.BLUE} >{Colors.RESET} '))
                print()

                # if is a invalid option
                if opt not in opts.keys():
                    print(f"{Colors.RED}[!]{Colors.RESET} Option not Allowed!\n")

                # if is a valid option, then execute the method
                else:
                    opts[opt]()
                    break

        except Exception as e:
            print(e)
        
    def _add_freight(self):
        from gdrive_handler import create_gdrive_file
        file_path = input(f'{Colors.PURPLE}[+]{Colors.RESET} Nome do arquivo (.xlsx)> ')
        if '.xlsx' not in file_path:
            new_file_path = file_path + '.xlsx'
        file = Path(new_file_path)

        try:
            file = file.resolve(strict=True)
        except FileNotFoundError:
            file = Path(file_path+'.xls')
            file = file.resolve(strict=True)
        
        if file.exists():
            link = create_gdrive_file(file_path, str(file))

        infos = {
            'origem': get_input('Origem: '),
            'destino': get_input('Destino: '),
            'client': get_input('Nome do cliente: '),
            'link': link
        }
        msg = create_freight(**infos)
        send2trash.send2trash(str(file))
        print(f'{Colors.GREEN}\n[+]{Colors.RESET} Created!\n')
        print(f'{Colors.BLUE}[-]{Colors.RESET} Link to access:\n', link)
        resp = input('Exit? [y/N]').lower()
        if resp == 'y':
            return
        else:
            self._add_freight()

    def _query_freight(self) -> str:
        infos = {
            'origem': get_input('Origem: '),
            'destino': get_input('Destino: '),
            'client': get_input('Nome do cliente: ')
            } 
        msg = query_freight(**infos) 
        print(f'{Colors.BLUE}[+] {Colors.RESET}Link to access:\n')
        for x in msg:
            print(x)

Menu()