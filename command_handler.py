#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

from command import Command


class CommandHandlerExeption(Exception):
    pass


class CommandHandler():
    def __init__(self):
        self.__commands__ = {}

    def add_command(self, name, value, nargs='?', default=None, question=None, ctype=str):
        if(nargs != '?' and nargs > 1 and default is not None):
            raise CommandHandlerExeption(
                "Cannot combine default with nargs > 1")
        elif(isinstance(ctype, tuple)):
            raise CommandHandlerExeption(
                "ctype must be a type or tuple of types")

        self.__commands__[name] = Command(
            name, value, nargs, default, question)

    def contains(self, name):
        return name in self.__commands__

    def get(self, name):
        if(name in self.__commands__):
            return self.__commands__[name]

        return Command()

    def parse(self, input):
        iargs = input.split()

        if(self.contains(iargs[0])):
            command = self.get(iargs[0])

            if(len(iargs) == 2):
                if(isinstance(iargs[1], command.ctype())):
                    raise CommandHandlerExeption(
                        "Type of argument should be %s" % command.ctype())

            if(command.nargs() == '?'):
                if(len(iargs) > 2):
                    raise CommandHandlerExeption(
                        "Too many arguments. Only one argument may be passed.")
            elif(len(iargs) > (command.nargs() + 1)):
                raise CommandHandlerExeption("Too many arguments. "
                                             "Command requires %s argument(s)" %
                                             self.get(iargs[0]).nargs())
            elif(len(iargs) < (command.nargs() + 1)):
                raise CommandHandlerExeption("Too few arguments. "
                                             "Command requires %s argument(s)" %
                                             self.get(iargs[0]).nargs())

            # append arguments to command value
            if(len(iargs) > 1):
                command.set_args(
                    bytes(' ' + ' '.join(a for a in iargs[1::]), 'utf-8'))
            # set default if no args presented
            elif(command.default()):
                command.set_args(bytes(' ' + str(command.default()), 'utf-8'))

            return command
        else:
            raise CommandHandlerExeption("Unknown command %s" % iargs[0])
