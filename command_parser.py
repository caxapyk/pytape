#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

from command import Command


class CommandParserExeption(Exception):
    pass


class CommandParser():
    def __init__(self):
        self.__commands = {}

    def add_command(self, name, value, nargs='?', default=[], question=None, type=str, help=''):
        if (isinstance(nargs, str)) and (nargs != '?'):
            raise CommandParserExeption(
                "Parameter nargs must be a number or ?.")
        if not isinstance(default, list):
            raise CommandParserExeption(
                "Parameter default must be a list type.")
        if not type in (int, str):
            raise CommandParserExeption(
                "Unknown type. Only strings and integers are allowed.")

        self.__commands[name] = Command(
            name, value, nargs, default, question, type, help)

    def add_external_command(self, name, help=''):
        """ Exteranal commands will just be returned to console """
        self.add_command(name, bytes(name, 'utf-8'), nargs=0, help=help)

    def contains(self, name):
        return name in self.__commands

    def get(self, name):
        if name in self.__commands:
            return self.__commands[name]

        return Command()

    def parse(self, input):
        if not input:
            return None

        iargs = input.split()

        if self.contains(iargs[0]):
            command = self.get(iargs[0])
            if command is None:
                return None

            c_args = []

            if len(iargs) > 1:
                c_args += iargs[1::]
            elif command.default() is not None:
                c_args += list(command.default())

            self.validate_args(command, c_args)

            # append arguments to command value
            command.set_args(' '.join(str(a) for a in c_args))

            return command
        elif iargs[0] == 'help':
            self.print_help()
            return None
        else:
            raise CommandParserExeption("Unknown command %s." % iargs[0])

    def validate_args(self, command, args):
        if isinstance(command.nargs(), str):
            if len(args) > 1:  # nargs='?'
                raise CommandParserExeption(
                    "Too many arguments. Only one argument may be passed.")
        elif isinstance(command.nargs(), int):
            if len(args) > command.nargs():
                raise CommandParserExeption("Too many arguments. "
                                            "Command requires %s argument(s)" %
                                            command.nargs())
            elif len(args) < command.nargs():
                raise CommandParserExeption("Too few arguments. "
                                            "Command requires %s argument(s)" %
                                            command.nargs())

        # check arguments types
        i = 0
        while i < len(args):
            if command.type() == int:
                try:
                    int(args[i])
                except ValueError:
                    raise CommandParserExeption(
                        "Type of argument %s should be a number." % (i + 1))
            i += 1

    def print_help(self):
        for name in self.__commands:
            command = self.get(name)

            print(
                "{command}\t\t{help}".format(
                    command=command.name(), help=command.help()))
