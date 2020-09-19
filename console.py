from command_parser import CommandParser, CommandParserExeption


class IConsole():
    def __init__(self):
        self.c_parser = CommandParser()
        # backup
        self.c_parser.add_command('backup', b'BACKUP', nargs='?',
                                  help="Backup directory to tape "
                                  "in append mode")
        # backward
        self.c_parser.add_command('backward', b'BACKWARD', nargs='?',
                                  default=[1],
                                  help="Go to COUNT records backward, default COUNT is 1")
        # config
        self.c_parser.add_command('config', b'BACKWARD', nargs=0,
                                  help="Show server configuration")
        # erase
        self.c_parser.add_command('erase', b'ERASE', nargs=0,
                                  question="Erase can take a lot of time, "
                                  "do you want to continue",
                                  help="Erase tape")
        # list
        self.c_parser.add_command('list', b'LIST', nargs=5,
                                  help="Show files on current record")
        # rewind
        self.c_parser.add_command('rewind', b'REWIND', nargs=0,
                                  question="Do you wand to rewind tape to "
                                  "beginning-of-the-tape",
                                  help="Rewind to beginning-of-the-tape "
                                  "(BOT)")
        # status
        self.c_parser.add_command('status', b'STATUS', nargs=0,
                                  help="Show tape status")
        # toward
        self.c_parser.add_command('toward', b'TOWARD', nargs='?',
                                  default=[1],
                                  type=int,
                                  help="Go to COUNT records toward, default COUNT is 1")
        # wind
        self.c_parser.add_command('wind', b'WIND', nargs=0,
                                  question="Do you wand to wind tape to "
                                  "end-of-the-tape",
                                  help="Wind to end-of-the-tape (EOT)")

        # external commands
        self.c_parser.add_external_command('connect', help="Connect to server")
        self.c_parser.add_external_command('exit', help="Exit programm")

    def run(self):
        """ Start interactive console"""
        while True:
            cmd = input("> ")
            if len(cmd) > 0:
                try:
                    command = self.c_parser.parse(cmd)
                except CommandParserExeption as e:
                    print(e)
                    continue
            else:
                continue

            if command is not None:
                if command.question():
                    i = input("%s [Y/n]? " % command.question())
                    if (i != '') and (i != 'Y') and (i != 'y'):
                        continue

                statement = command.value()
                if command.arguments() is not None:
                    statement += command.arguments()

                return statement

            continue
