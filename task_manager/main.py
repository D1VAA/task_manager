from src.controller.input_handler import InputHandler
from src.controller.initializer import initializer

initializer()
menu = InputHandler()
menu.cmd_input()