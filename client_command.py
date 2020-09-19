from command import Command


class ClientCommand(Command):
    def __init__(self, name, value, nargs='?', default=[], question=None, type=str, help=''):
        super().__init__(name, value, nargs, default, question, type, help)
