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
            print("Connecting to server...")
            self.sock.connect((host, port))
        except socket.error as e:
            print("Failed to connect to server %s:%s. "
                  "Error: %s" % (host, port, e))
            sys.exit()

        self.__is_connected = True
        print("Connection established!")

    def hostname(self):
        return self.__hostname

    def port(self):
        return self.__port

    def _exec(self, command):
        if command in self.__internal_commands:
            getattr(self, self.__internal_commands[command])()
        else:
            if self.__is_connected:
                self.__send_remote(command)
            else:
                print("Not connected to server")

    def __disconnect(self):
        self.sock.close()

    def __send_remote(self, command):
        try:
            self.sock.sendall(command)
            response = self.sock.recv(1024)
            response = response.decode('utf-8')

            print(response)

        except socket.error as e:
            print("Failed to send command. Error: %s" % e)

    # commands

    def _c_connect(self):
        host = input("Enter server hostname [%s]: " % self.__hostname)
        if(len(host) == 0):
            host = self.__hostname
        port = input("Enter server port [%s]: " % self.__port)
        if(len(port) == 0):
            port = self.__port

        try:
            port = int(port)
            self.connect(host, port)
        except ValueError:
            print("Connection error. Port must be a number.")
        except OverflowError:
            print("Connection error. Port must be 0-65535.")

    def _c_exit(self):
        if self.__is_connected:
            self.__disconnect()
            sys.exit()
