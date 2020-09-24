import asyncio
import sys

from command_parser import CommandParser, CommandParserException
from client_command import ClientCommand
from remote_command import RemoteCommand


class IConsole():
    def __init__(self):
        self.c_parser = CommandParser()

    def set_command_parser(self, parser):
        self.c_parser = parser

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
