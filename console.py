from command_parser import CommandParser, CommandParserException
from client_command import ClientCommand
from remote_command import RemoteCommand


class IConsole():
    def __init__(self):
        self.c_parser = CommandParser()
        # backup
        self.c_parser.add_command(
            RemoteCommand('backup', b'BACKUP', nargs='?',
                          help="Backup directory to tape "
                          "in append mode"))
        # backward
        self.c_parser.add_command(
            RemoteCommand('backward', b'BACKWARD', nargs='?',
                          default=[1],
                          type=int,
                          help="Go to COUNT records backward, default COUNT is 1"))
        # config
        self.c_parser.add_command(
            RemoteCommand('config', b'CONFIG', nargs=0,
                          help="Show server configuration"))
        # erase
        self.c_parser.add_command(
            RemoteCommand('erase', b'ERASE', nargs=0,
                          question="Erase can take a lot of time, do you want to continue",
                          help="Erase tape"))
        # list
        self.c_parser.add_command(
            RemoteCommand('list', b'LIST', nargs=0,
                          help="Show files on current record"))
        # rewind
        self.c_parser.add_command(
            RemoteCommand('rewind', b'REWIND', nargs=0,
                          question="Do you wand to rewind tape to beginning-of-the-tape",
                          help="Rewind to beginning-of-the-tape (BOT)"))
        # status
        self.c_parser.add_command(
            RemoteCommand('status', b'STATUS', nargs=0,
                          help="Show tape status"))
        # toward
        self.c_parser.add_command(
            RemoteCommand('toward', b'TOWARD', nargs='?',
                          default=[1],
                          type=int,
                          help="Go to COUNT records toward, default COUNT is 1"))
        # wind
        self.c_parser.add_command(
            RemoteCommand('wind', b'WIND', nargs=0,
                          question="Do you wand to wind tape to end-of-the-tape",
                          help="Wind to end-of-the-tape (EOT)"))

        # client commands
        self.c_parser.add_command(
            ClientCommand('connect', b'connect', help="Connect to server"))
        self.c_parser.add_command(
            ClientCommand('exit', b'exit', help="Exit the programm"))

    def run(self):
        """ Start interactive console"""
        while True:
            cmd = input("> ")
            if len(cmd) > 0:
                try:
                    command = self.c_parser.parse(cmd)
                except CommandParserException as e:
                    print(e)
                    continue
            else:
                continue

            if command is not None:
                if command.question():
                    i = input("%s [Y/n]? " % command.question())
                    if (i != '') and (i != 'Y') and (i != 'y'):
                        continue

                return command

            continue
