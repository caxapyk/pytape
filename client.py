#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import asyncio
import socket
import sys

from command_parser import CommandParser, CommandParserException
from console import IConsole
from client_command import ClientCommand
from remote_command import RemoteCommand


class Client():
    def __init__(self):
        self.__pytape = """
############################################################
#                    WELLCOME TO PYTAPE                    #
#    Client-Server GNU mt/tar utils wrapper to remote      #
#    backup, restore and manage tape device in Linux,      #
#        written on Python asyncio network module.         #
############################################################

            """
        self.__internal_commands = {
            b'about': '_c_about',
            b'connect': '_c_connect',
            b'exit': '_c_exit'
        }

        self.__hostname = 'localhost'
        self.__port = 50077

        self.__is_connected = False

        self.__parser = CommandParser()
        # backup
        self.__parser.add_command(
            RemoteCommand('backup', b'BACKUP', nargs='?',
                          help="Backup PATH on the tape in append mode, "
                          "default PATH is configured on server"))
        # backward
        self.__parser.add_command(
            RemoteCommand('backward', b'BACKWARD', nargs='?',
                          default=[1],
                          type=int,
                          help="Go to COUNT records backward, default COUNT=1"))
        # config
        self.__parser.add_command(
            RemoteCommand('config', b'CONFIG', nargs=0,
                          help="Show server configuration"))
        # erase
        self.__parser.add_command(
            RemoteCommand('erase', b'ERASE', nargs=0,
                          question="Erase can take a lot of time (~2.5hours), do you want to continue",
                          help="Erase the tape from current record"))

        # eject
        self.__parser.add_command(
            RemoteCommand('eject', b'EJECT', nargs=0,
                          question="Do you want to eject the tape?",
                          help="Eject the tape"))
        # error
        self.__parser.add_command(
            RemoteCommand('error', b'LASTERR', nargs=0,
                          help="Show last server error"))

        # list
        self.__parser.add_command(
            RemoteCommand('list', b'LIST', nargs=0,
                          help="Show files on current record"))

        # record
        self.__parser.add_command(
            RemoteCommand('record', b'RECORD', nargs=0,
                          help="Show current record number"))
        # restore
        self.__parser.add_command(
            RemoteCommand('restore', b'RESTORE', nargs='?',
                          question="Do you want to restore current record",
                          help="Restore current record to the PATH, "
                          "default PATH is configured on server"))

        # rewind
        self.__parser.add_command(
            RemoteCommand('rewind', b'REWIND', nargs=0,
                          question="Do you wand to rewind tape to beginning-of-the-tape",
                          help="Rewind to beginning-of-the-tape (BOT)"))
        # status
        self.__parser.add_command(
            RemoteCommand('status', b'STATUS', nargs=0,
                          help="Show tape status"))
        # toward
        self.__parser.add_command(
            RemoteCommand('toward', b'TOWARD', nargs='?',
                          default=[1],
                          type=int,
                          help="Go to COUNT records toward, default COUNT=1"))
        # wind
        self.__parser.add_command(
            RemoteCommand('wind', b'WIND', nargs=0,
                          question="Do you wand to wind tape to end-of-the-tape",
                          help="Wind to end-of-the-tape (EOT)"))

        # client commands
        self.__parser.add_command(
            ClientCommand('about', b'about', help="About programm"))
        self.__parser.add_command(
            ClientCommand('connect', b'connect', help="Connect to server"))
        self.__parser.add_command(
            ClientCommand('exit', b'exit', help="Exit the programm"))

        self.__iconsole = IConsole()
        self.__iconsole.set_command_parser(self.__parser)

    async def run(self, host=None, port=None):
        self.__iconsole.printf(self.__pytape)

        if port:
            self.__port = port
        if host:
            self.__hostname = host
            conn = self.connect(host, self.__port)

            try:
                # Wait for 3 seconds, then raise TimeoutError
                await asyncio.wait_for(conn, timeout=5)
            except asyncio.TimeoutError:
                print("Connection timeout")
                sys.exit(1)

        while True:
            command = self.__iconsole.run()
            if isinstance(command, ClientCommand):
                await self._exec(command)
            elif isinstance(command, RemoteCommand):
                response = await self.send(command)
                if response:
                    self.__iconsole.printf(response.decode())

    async def connect(self, host, port):
        try:
            reader, writer = await asyncio.open_connection(
                host, int(port))

            writer.write(b'HELLO')
            response = await reader.read(64)
            writer.close()

            if response == b'HELLO':
                self.__is_connected = True
                self.__iconsole.printf("Connection established!")

        except socket.error as e:
            self.__is_connected = False
            self.__iconsole.printf("Failed to create connection (%s:%s). "
                                   "Error: %s" % (host, port, e))
        except ValueError:
            self.__is_connected = False
            self.__iconsole.printf("Connection error. Port must be 0-65535.")

    async def send(self, command):
        if self.__is_connected:
            try:
                statement = command.value()
                if len(command.arguments()) > 0:
                    statement += b' ' + command.arguments()

                reader, writer = await asyncio.open_connection(
                    self.__hostname, self.__port)

                writer.write(statement)
                response = asyncio.create_task(reader.read(65536))
                read = asyncio.create_task(
                    self.__iconsole.print_wait(response))

                await response
                await read

                writer.close()

                return response.result()

            except socket.gaierror as e:
                self.__iconsole.printf("Socket address error. Error: %s" % e)
            except OSError as e:
                self.__iconsole.printf("Failed to send command. Error: %s" % e)
        else:
            self.__iconsole.printf("Not connected to server")

    async def _exec(self, command):
        funct = getattr(
            self, self.__internal_commands[command.value()])
        await funct(command.arguments())

    # commands

    async def _c_connect(self, args):
        host = self.__hostname
        port = self.__port

        if len(args) > 0:
            # try to split host:port
            split = args.decode().split(':')
            if len(split) == 2:
                host = split[0]
                port = split[1]
            else:
                host = args
        else:
            promt_host = input(
                "Enter server hostname [%s]: " % self.__hostname)
            if len(promt_host) > 0:
                host = promt_host
            promt_port = input("Enter server port [%s]: " % self.__port)
            if len(promt_port) > 0:
                port = promt_port

        port = int(port)
        await self.connect(host, port)

    async def _c_exit(self, args):
        sys.exit()

    async def _c_about(self, args):
        self.__iconsole.printf("""
Client-Server GNU mt/tar utils wrapper to remote backup, restore
and manage tape device in Linux, written on Python asyncio network module.

Sakharuk Alexander, 2020 <saharuk.alexander@gmail.com>
Licensed under GNU GENERAL PUBLIC LICENSE Version 3
            """)
