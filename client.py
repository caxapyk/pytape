#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import socket
import sys


class Client():
    def __init__(self):
        self.__internal_commands = {
            b'connect': '_c_connect',
            b'exit': '_c_exit'
        }

        self.__hostname = 'localhost'
        self.__port = 50077

        self.__is_connected = False

    def connect(self, host, port):
        # Create an AF_INET, STREAM socket (TCP)
        try:
            self.sock = socket.socket(socket.AF_INET,
                                      socket.SOCK_STREAM)
        except socket.error as e:
            print("Failed to create socket. Error: %s" % e)
            sys.exit()

        # Connect to server
        try:
            self.sock.connect((host, port))

            self.__is_connected = True
            print("Connection established!")
        except socket.error as e:
            print("Failed to connect to server %s:%s. "
                  "Error: %s" % (host, port, e))

    def hostname(self):
        return self.__hostname

    def port(self):
        return self.__port

    def _exec(self, command):
        getattr(
            self, self.__internal_commands[command.value()])(
            command.arguments())

    def __disconnect(self):
        self.sock.close()

    def send(self, command):
        if self.__is_connected:
            try:
                statement = command.value()
                if len(command.arguments()) > 0:
                    statement += b' ' + command.arguments()

                print(statement)

                self.sock.sendall(statement)
                response = self.sock.recv(1024)
                response = response.decode('utf-8')

                print(response)

            except socket.error as e:
                print("Failed to send command. Error: %s" % e)
        else:
            print("Not connected to server")

    # commands

    def _c_connect(self, args):
        host = self.__hostname
        port = self.__port

        try:
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
            self.connect(host, port)
        except ValueError:
            print("Connection error. Port must be a number.")
        except OverflowError:
            print("Connection error. Port must be 0-65535.")

    def _c_exit(self, args):
        if self.__is_connected:
            self.__disconnect()
        sys.exit()
