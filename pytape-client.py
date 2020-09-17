#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import argparse
import socket
import sys

ERR_CODE = '0x01'


class Client():
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

    def send_command(self, command):
        try:
            self.sock.sendall(command)
            response = self.sock.recv(1024)
            response = response.decode('utf-8')

            if(response == ERR_CODE):
                error = self.send_command(b'LASTERR')
                return "Remote command executed with errors.\n\n%s" % error

            return response

        except socket.error as e:
            print("Failed to send command. Error: %s" % e)
            sys.exit()


def main():
    parser = argparse.ArgumentParser(
        description='PyTape Client 2020 Sakharuk Alexander')
    parser.add_argument('-s', '--host', action='store',
                        default='localhost', help='Server hostname')
    parser.add_argument('-p', '--port', action='store',
                        default=50077, help='Server port')

    args = parser.parse_args()

    cmd_parser = argparse.ArgumentParser(
        description='PyTape Client 2020 Sakharuk Alexander')

    cmd_parser.add_argument('command', choices=[
        'backup',
        'backward',
        'erase',
        'exit',
        'help',
        'lerror',
        'list',
        'rewind',
        'status',
        'toward',
        'wind'])

    cmd_parser.add_argument('param', nargs='?', default=1, type=int)

    client = Client()
    client.connect(args.host, args.port)

    # Start interactive console
    while True:
        cmd = input("> ")
        try:
            if(len(cmd) > 0):
                iargs = cmd_parser.parse_args(cmd.split())
            else:
                continue
        except SystemExit:
            continue

        if iargs.command == 'backup':
            bdir = client.send_command(b'GETBDIR')
            cmd = input("Backup directory on server [%s]: " % bdir)
            if(cmd):
                print(client.send_command(
                    bytes('BACKUPSPECDIR %s %s' % (cmd, cmd), 'utf-8')))
            else:
                print(client.send_command(b'BACKUP'))
        elif iargs.command == 'backward':
            print(client.send_command(
                bytes('BACKWARD %s' % iargs.param, 'utf-8')))
        elif iargs.command == 'erase':
            cmd = input(
                "Erase can take a lot of time, "
                "do you want to continue [Y/n]? ")
            if(cmd == "" or cmd == "Y" or cmd == "y"):
                print(client.send_command(b'ERASE'))
            else:
                continue
        elif iargs.command == 'lerror':
            print(client.send_command(b'LASTERR'))
        elif iargs.command == 'list':
            print(client.send_command(b'LIST'))
        elif iargs.command == 'rewind':
            cmd = input(
                "Do you wand to rewind tape to beginning-of-the-tape [Y/n]? ")
            if(cmd == "" or cmd == "Y" or cmd == "y"):
                print(client.send_command(b'REWIND'))
            else:
                continue
        elif iargs.command == 'status':
            print(client.send_command(b'STATUS'))
        elif iargs.command == 'toward':
            print(client.send_command(
                bytes('TOWARD %s' % iargs.param, 'utf-8')))
        elif iargs.command == 'wind':
            cmd = input(
                "Do you wand to wind tape to end-of-the-tape [Y/n]? ")
            if(cmd == "" or cmd == "Y" or cmd == "y"):
                print(client.send_command(b'WIND'))
            else:
                continue
        elif iargs.command == 'exit':
            client.disconnect()
            break
        elif iargs.command == 'help':
            cmd_parser.print_help()
            continue

        continue


if __name__ == "__main__":
    main()
