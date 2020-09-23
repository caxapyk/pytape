import asyncio
import sys

from command_parser import CommandParser, CommandParserException
from client_command import ClientCommand
from remote_command import RemoteCommand


class IConsole():
    def __init__(self):
        self.c_parser = CommandParser()
        # backup
        self.c_parser.add_command(
            RemoteCommand('backup', b'BACKUP', nargs='?',
                          help="Backup PATH on the tape in append mode, "
                          "default PATH is configured on server"))
        # backward
        self.c_parser.add_command(
            RemoteCommand('backward', b'BACKWARD', nargs='?',
                          default=[1],
                          type=int,
                          help="Go to COUNT records backward, default COUNT=1"))
        # config
        self.c_parser.add_command(
            RemoteCommand('config', b'CONFIG', nargs=0,
                          help="Show server configuration"))
        # erase
        self.c_parser.add_command(
            RemoteCommand('erase', b'ERASE', nargs=0,
                          question="Erase can take a lot of time (~2.5hours), do you want to continue",
                          help="Erase the tape from current record"))

        # eject
        self.c_parser.add_command(
            RemoteCommand('eject', b'EJECT', nargs=0,
                          question="Do you want to eject the tape?",
                          help="Eject the tape"))
        # error
        self.c_parser.add_command(
            RemoteCommand('error', b'LASTERR', nargs=0,
                          help="Show last server error"))

        # list
        self.c_parser.add_command(
            RemoteCommand('list', b'LIST', nargs=0,
                          help="Show files on current record"))

        # record
        self.c_parser.add_command(
            RemoteCommand('record', b'RECORD', nargs=0,
                          help="Show current record number"))
        # restore
        self.c_parser.add_command(
            RemoteCommand('restore', b'RESTORE', nargs='?',
                          question="Do you want to restore current record",
                          help="Restore current record to the PATH, "
                          "default PATH is configured on server"))

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
                          help="Go to COUNT records toward, default COUNT=1"))
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
            cmd = input("\n> ")
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

    def printf(self, value):
        print("\r{}".format(value), end='', flush=True)

    async def print_wait(self, depended, value="Please wait"):
        i = 0
        dots = 5
        while not depended.done():
            count = i % (dots + 2)
            end = '.' * count + '\r'

            if count == (dots + 1):
                end = ' ' * (dots + 2) + '\r'

            print("\r{}".format(value), end=end, flush=True)
            await asyncio.sleep(0.75)
            i += 1

        # clear output
        print("%s" % ' ' * (len(value) + dots), end='\r', flush=True)
