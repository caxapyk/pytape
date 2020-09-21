#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import asyncio
import socket
import sys

from console import IConsole
from client_command import ClientCommand
from remote_command import RemoteCommand


class Client():
    def __init__(self):
        self.__internal_commands = {
            b'connect': '_c_connect',
            b'exit': '_c_exit'
        }

        self.__hostname = 'localhost'
        self.__port = 50077

        self.__is_connected = False

        self.__reader = None
        self.__writer = None

        self.__iconsole = IConsole()

    async def run(self, host=None, port=None):
        if port:
            self.__port = port
        if host:
            self.__hostname = host
            await self.connect(host, self.__port)

        while True:
            command = self.__iconsole.run()
            if isinstance(command, ClientCommand):
                await self._exec(command)
            elif isinstance(command, RemoteCommand):
                await self.send(command)

    async def connect(self, host, port):
        try:
            self.__reader, self.__writer = await asyncio.open_connection(
                host, int(port))

            self.__writer.write(b'HELLO')
            response = await self.__reader.read(64)
            self.__writer.close()

            if response == b'HELLO':
                self.__is_connected = True
                self.__iconsole.print("Connection established!")

        except socket.error as e:
            self.__iconsole.print("Failed to create connection (%s:%s). "
                  "Error: %s" % (host, port, e))
        except ValueError:
            self.__iconsole.print("Connection error. Port must be 0-65535.")

    async def _exec(self, command):
        await getattr(
            self, self.__internal_commands[command.value()])(
            command.arguments())

    async def send(self, command):
        if self.__is_connected:
            try:
                statement = command.value()
                if len(command.arguments()) > 0:
                    statement += b' ' + command.arguments()

                self.__reader, self.__writer = await asyncio.open_connection(self.__hostname, self.__port)

                self.__writer.write(statement)
                response = await self.__reader.read(8192)

                self.__iconsole.print(response)

            except socket.gaierror as e:
                self.__iconsole.print("Failed to send command. Error: %s" % e)
        else:
            self.__iconsole.print("Not connected to server")

    # commands

    async def _c_connect(self, args):
        host = self.__hostname
        port = self.__port

        if len(args) > 0:
            # try to split host:port
            split = args.decode('utf-8').split(':')
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
