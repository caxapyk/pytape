#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#


class CommandException(Exception):
    pass


class Command():
    def __init__(self, name, value, nargs='?', default=[], question=None, type=str, help=''):
        if (isinstance(nargs, str)) and (nargs != '?'):
            raise CommandException(
                "Parameter nargs must be a number or ?.")
        if not isinstance(default, list):
            raise CommandException(
                "Parameter default must be a list type.")
        for def_value in default:
            if not isinstance(def_value, type):
                raise CommandException(
                    "All value types for default list must be %s" % type)
        if not type in (int, str):
            raise CommandException(
                "Unknown type. Only strings and integers are allowed.")

        self.__name = name
        self.__value = value
        self.__nargs = nargs
        self.__default = default
        self.__question = question
        self.__type = type
        self.__help = help

        self.__c_args = b''

    def arguments(self):
        return self.__c_args

    def set_args(self, args):
        self.__c_args = b''
        if(args):
            self.__c_args = bytes(str(args), 'utf-8')

    def name(self):
        return self.__name

    def value(self):
        return self.__value

    def nargs(self):
        return self.__nargs

    def default(self):
        return self.__default

    def question(self):
        return self.__question

    def type(self):
        return self.__type

    def help(self):
        return self.__help
