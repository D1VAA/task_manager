from pathlib import Path


from utils.imports import (
    Colors,
    create_freight,
    get_unique_values,
    query_freight,
)
import customtkinter as ctk
from customtkinter import filedialog


def open_file_dialog() -> tuple[str, ...]:
    root = ctk.CTk()
    root.withdraw()

    file_path = filedialog.askopenfilenames(
        title="Selecione um arquivo",
        filetypes=[("Todos os arquivos", "*"), ("Excel", "*.xlsx")],
    )
    assert isinstance(file_path, tuple)
    return file_path


def get_input(msg, allow_empty: bool = True):
    print()
    while True:
        obj = input(f"{Colors.PURPLE}[-]{Colors.RESET} {msg}").lower().rstrip()
        if not allow_empty:
            pass
        else:
            return obj


class Menu:
    def __init__(self):
        self.menu()

    def _show_menu_options(self):
        data = f"""
        \r-------------------------------------------------------------
        \r\t{Colors.RED}[1] {Colors.YELLOW}Adicionar um novo frete.
        \r\t{Colors.RED}[2] {Colors.YELLOW}Consultar um frete da base.
        \r\t{Colors.RED}[3] {Colors.YELLOW}Mostrar as opções.
          {Colors.RESET}
        """
        print(data)

    def menu(self):
        opts = {
            1: self._add_freight,
            2: self._query_freight,
            3: self.show_options,
        }

        while True:
            self._show_menu_options()
            try:
                opt = int(
                    input(f"Choose an option{
                          Colors.BLUE} >{Colors.RESET} ")
                )
                print()
                if opt in opts.keys():
                    opts[opt]()

                else:
                    print(f"{Colors.RED}[!]{
                          Colors.RESET} Option not Allowed!\n")

            except KeyboardInterrupt:
                print(f"\n\n{Colors.RED}[+]{Colors.RESET} Leaving...")
                break

            except ValueError:
                print(
                    "Opção inválida."
                    "\nSe estiver tentando sair, utilize o atalho CTRL+C"
                )

            except Exception as e:
                print(e)

    def _add_freight_to_file(self, file: Path):
        with open("to_register.txt", "a") as register_file:
            line_to_add = f"""+ Path: {file.as_posix()} - Name:{file.name}"""
            register_file.write(line_to_add)

    def _add_freight(self):
        from modules.gdrive_handler import create_gdrive_file

        file_path = open_file_dialog()

        def _get_info_and_upload_freight(path):
            file = Path(path)
            link_to_download = create_gdrive_file(file.name, str(file))
            print(f"+ File: {file.name}", end="\n")
            print(
                f"{Colors.BLUE}[+]{Colors.RESET} Preencha os dados do frete:")

            infos = {
               "origem": get_input("Origem: "),
               "destino": get_input("Destino: "),
               "client": get_input("Nome do cliente: "),
            }
            create_freight(**infos)

            print(f"{Colors.GREEN}\n[+]{Colors.RESET} Created!\n")
            print(
                f"{Colors.BLUE}[-]{Colors.RESET} Link to access:\n",
                link_to_download
            )
            answer = input(
                "Já foi preenchido na planilha de prospecções?[S/N] "
                )
            if not answer == ["y", "yes", "sim", "s"]:
                self._add_freight_to_file(file)

            return link_to_download

        if isinstance(file_path, tuple):
            for path in file_path:
                _get_info_and_upload_freight(path)

    def _query_freight(self):
        infos = {
            "origem": get_input("Origem: "),
            "destino": get_input("Destino: "),
            "client": get_input("Nome do cliente: "),
        }
        freightobj_list = query_freight(**infos)

        # Verifica se a consulta retornou uma mensagem
        if isinstance(freightobj_list, str):
            print(freightobj_list)
            return

        else:
            # Loop para printar todos os resultados
            for cont, freight_obj in enumerate(freightobj_list):
                print(
                    f'\n{"-"*10} {Colors.RED}{cont +
                                              1}º{Colors.RESET} {"-"*10} ',
                    end="\n",
                )
                print(
                    f"{Colors.YELLOW}{freight_obj.origem.title()} "
                    f"x {freight_obj.destino.title()} - "
                    f"{freight_obj.client.title()}{Colors.RESET}",
                    end="\n\n",
                )
                print(
                    f"{Colors.BLUE}[+]{Colors.RESET} {freight_obj.link}",
                    end="\n\n"
                )


Menu()
