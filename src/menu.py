from utils.colors import Colors
from freight_database.crud_database import create_freight, query_freight, get_unique_values
from pathlib import Path
import send2trash
from modules.todo import Todo

def get_input(msg, allow_empty: bool=True):
    print()
    while True:
        obj = input(f'{Colors.PURPLE}[-]{Colors.RESET} {msg}').lower().rstrip()
        if allow_empty == False:
            pass
        else:
            return obj 

class Menu(Todo):
    def __init__(self):
        self.menu()
    
    def _show_menu_options(self):
        data = f'''
        \r-------------------------------------------------------------
        \r\t{Colors.RED}[1] {Colors.YELLOW}Adicionar um novo frete a base de dados.
        \r\t{Colors.RED}[2] {Colors.YELLOW}Consultar um frete da base.
        \r\t{Colors.RED}[3] {Colors.YELLOW}Mostrar as opções.
        \r\t{Colors.RED}[4] {Colors.YELLOW}Gerenciador de tasks.
          {Colors.RESET}
        '''
        print(data)
    
    def menu(self):
        opts = {1: self._add_freight, 
                2: self._query_freight, 
                3: self.show_options, 
                4: super().__init__}

        while True:
            self._show_menu_options()
            try:
                opt = int(input(f'Choose an option{Colors.BLUE} >{Colors.RESET} '))
                print()

                # if is a invalid option
                if opt not in opts.keys():
                    print(f"{Colors.RED}[!]{Colors.RESET} Option not Allowed!\n")

                # if is a valid option, then execute the method
                else:
                    opts[opt]()
            except KeyboardInterrupt:
                print(f"\n\n{Colors.RED}[+]{Colors.RESET} Leaving...")
                break
            except Exception as e:
                print(e)
    
    def _add_freight(self):
        from modules.gdrive_handler import create_gdrive_file
        file_path = get_input('Nome do Arquivo (.xlsx or .xls)> ')
        if '.xlsx' not in file_path:
            new_file_path = file_path + '.xlsx'
        file = Path(new_file_path)

        try:
            file = file.resolve(strict=True)

        except FileNotFoundError:
            file = Path(file_path+'.xls')
            file = file.resolve(strict=True)
        
        if file.exists():
            link_to_download = create_gdrive_file(file_path, str(file))

        infos = {
            'origem': get_input('Origem: '),
            'destino': get_input('Destino: '),
            'client': get_input('Nome do cliente: '),
        }

        create_freight(**infos)
        send2trash.send2trash(str(file))

        print(f'{Colors.GREEN}\n[+]{Colors.RESET} Created!\n')
        print(f'{Colors.BLUE}[-]{Colors.RESET} Link to access:\n', link_to_download)
        resp = input('Exit? [y/N]').lower()
        if resp == 'y':
            return
        else:
            self._add_freight()

    def _query_freight(self):
        infos = {
            'origem': get_input('Origem: '),
            'destino': get_input('Destino: '),
            'client': get_input('Nome do cliente: ')
        } 
        freightobj_list = query_freight(**infos) 
        for cont, freight_obj in enumerate(freightobj_list):
            print(f'\n{"-"*10} {Colors.RED}{cont+1}º{Colors.RESET} {"-"*10} ', end='\n')
            print(f'{Colors.YELLOW}{freight_obj.origem.title()} x {freight_obj.destino.title()}{Colors.RESET}',end='\n\n')
            print(f'{Colors.BLUE}[+]{Colors.RESET} {freight_obj.link}', end='\n\n')

    def show_options(self):
        or_col = get_unique_values("origem")
        dest_col = get_unique_values("destino")
        client_col = get_unique_values("client")
        strings = or_col + dest_col + client_col
        len_f = len(max(strings, key=len))
        format_string = f'|{{:^{len_f}}}|{{:^{len_f}}}|{{:^{len_f}}}|'
        print(format_string.format("Origem", "Destino", "Cliente"))
        print(format_string.format("------", "-------", "-------"))
        print(format_string.format("", "", ""))
        for x,y,z in zip(or_col, dest_col, client_col):
            print(format_string.format(x.title(), y.title(), z.title()))

Menu()
