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
                response = asyncio.create_task(reader.read(8192))
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
