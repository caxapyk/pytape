#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import socket
import sys

from command_handler import CommandHandler, CommandHandlerExeption


class Client():

    def __init__(self):
        self.c_handler = CommandHandler()
        self.c_handler.add_command('backup', b'BACKUP', nargs='?')
        self.c_handler.add_command('backward', b'BACKWARD', nargs='?', default=1, ctype=int)
        self.c_handler.add_command('config', b'BACKWARD', nargs=0)
        self.c_handler.add_command('erase', b'ERASE', nargs=0,
                                   question="Erase can take a lot of time, "
                                   "do you want to continue")
        self.c_handler.add_command('list', b'LIST', nargs=0)
        self.c_handler.add_command('rewind', b'REWIND', nargs=0,
                                   question="Do you wand to rewind tape "
                                   "to beginning-of-the-tape")
        self.c_handler.add_command('status', b'STATUS', nargs=0)
        self.c_handler.add_command('toward', b'TOWARD', nargs='?', default=1, ctype=int)
        self.c_handler.add_command('wind', b'WIND', nargs=0,
                                   question="Do you wand to wind tape "
                                   "to end-of-the-tape")

    def connect(self, host, port):
        # Create an AF_INET, STREAM socket (TCP)
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        except socket.error as e:
            print("Failed to create socket. Error: %s" % e)
            sys.exit()

        # Connect to server
        try:
            print("Connecting to server...")
            self.sock.connect((host, port))
        except socket.error as e:
            print("Failed to connect to server %s:%s. "
                  "Error: %s" % (host, port, e))
            sys.exit()

        print("Connection established!")

    def disconnect(self):
        self.sock.close()

    def console(self):
        """ Start interactive console"""
        while True:
            cmd = input("> ")
            if(len(cmd) > 0):
                try:
                    command = self.c_handler.parse(cmd)
                except CommandHandlerExeption as e:
                    print(e)
                    continue
            else:
                continue

            if(command.question()):
                i = input("%s [Y/n]? " % command.question())
                if(i != '' and i != 'Y' and i != 'y'):
                    continue

            statement = command.value()
            if(command.arguments() is not None):
                statement += command.arguments()

            self._send(statement)

            continue

    def print_help(self):
        print("help is here")

    def _send(self, command):
        try:
            self.sock.sendall(command)
            response = self.sock.recv(1024)
            response = response.decode('utf-8')

            print(response)

        except socket.error as e:
            print("Failed to send command. Error: %s" % e)
            sys.exit()
