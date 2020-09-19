#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

from command import Command


class CommandParserException(Exception):
    pass


class CommandParser():
    def __init__(self):
        self.__commands = []

    # def add_command(self, name, value, nargs='?', default=[], question=None, type=str, help=''):
    #    self.__commands[name] = Command(
    #        name, value, nargs, default, question, type, help)

    def add_command(self, command):
        if not isinstance(command, Command):
            raise CommandParserException(
                "Command should be an isinstance of Command Class")
        self.__commands.append(command)

    def contains(self, name):
        for command in self.__commands:
            if command.name() == name:
                return True

        return False

    def get(self, name):
        if self.contains(name):
            for command in self.__commands:
                if command.name() == name:
                    return command

        return None

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

            # set arguments string to command
            command.set_args(' '.join(str(a) for a in c_args))

            return command
        elif iargs[0] == 'help':
            self.print_help()
            return None
        else:
            raise CommandParserException("Unknown command %s." % iargs[0])

    def validate_args(self, command, args):
        if isinstance(command.nargs(), str):
            if len(args) > 1:  # nargs='?'
                raise CommandParserException(
                    "Too many arguments. Only one argument may be passed.")
        elif isinstance(command.nargs(), int):
            if len(args) > command.nargs():
                raise CommandParserException("Too many arguments. "
                                             "Command requires %s argument(s)" %
                                             command.nargs())
            elif len(args) < command.nargs():
                raise CommandParserException("Too few arguments. "
                                             "Command requires %s argument(s)" %
                                             command.nargs())

        # check arguments types
        i = 0
        while i < len(args):
            if command.type() == int:
                try:
                    int(args[i])
                except ValueError:
                    raise CommandParserException(
                        "Type of argument %s should be a number." % (i + 1))
            i += 1

    def print_help(self):
        for command in self.__commands:
            print(
                "{command}\t\t{help}".format(
                    command=command.name(), help=command.help()))
