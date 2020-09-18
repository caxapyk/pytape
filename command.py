#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#


class Command():
    def __init__(self, name, value, nargs='?', default=None, question=None, ctype=str):
        self.c_handler = {
            'default': default,
            'question': question,
            'name': name,
            'nargs': nargs,
            'value': value,
            'ctype': ctype
        }

        self.c_args = None

    def name(self):
        return self.c_handler['name']

    def nargs(self):
        return self.c_handler['nargs']

    def default(self):
        return self.c_handler['default']

    def question(self):
        return self.c_handler['question']

    def value(self):
        return self.c_handler['value']

    def ctype(self):
        return self.c_handler['ctype']

    def arguments(self):
        return self.c_args

    def set_args(self, args):
        self.c_args = args
