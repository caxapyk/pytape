#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import argparse
import os
import socket
import subprocess


class CommandHandler():
    # protocol commands
    C_PROTOCOL = {
        'STATUS': 'mt status',
        'STATUSTAPE': 'mt status {}',
        'BACKUP': '',
        'RESTORE': ''
    }

    def _exec(self, args):
        command = None

        if(args[0] in self.C_PROTOCOL):
            if(len(args) > 1):
                command = self.C_PROTOCOL[args[0]].format(*args[1::])
            else:
                command = self.C_PROTOCOL[args[0]]
        else:
            return b'Unknown command'

        with subprocess.Popen(command, shell=True,
                              stderr=subprocess.PIPE,
                              stdout=subprocess.PIPE) as proc:
            if proc:
                out = proc.stdout.read()
                stderr = proc.stderr.read()

                if (stderr):
                    out += stderr

            return out


class Server():
    def __init__(self, host, port):
        self.SERVER_HOST = host
        self.SERVER_PORT = port

    def run(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.bind((self.SERVER_HOST, self.SERVER_PORT))
            sock.listen(1)

            handler = CommandHandler()

            # main loop
            while True:
                try:
                    conn, addr = sock.accept()
                    print('Connected by', addr)

                    while True:
                        data = conn.recv(1024)
                        if not data:
                            break

                        args = data.decode('utf-8').split()
                        response = handler._exec(args)

                        conn.sendall(bytes(response))

                    conn.close()

                except socket.error as e:
                    conn.close()
                    print('Client connection error: %s' % e)

    def install(self):
        u = ("[Unit]\n"
             "Description=PyTape Server\n"
             "After=network.target\n"
             "\n"
             "[Service]\n"
             "\n"
             "ExecStart=/usr/bin/python3 '%s/pytape-server.py' --run\n"
             "ExecReload=/bin/kill -s HUP $MAINPID\n"
             "ExecStop=/bin/kill -s QUIT $MAINPID\n"
             "TimeoutSec=30\n"
             "Type=Simple\n"
             "Restart=always\n"
             "\n"
             "[Install]\n"
             "WantedBy=default.target\n" % os.getcwd())
        try:
            unit = open('/etc/systemd/system/pytape.service', 'w')
            unit.write(u)
            unit.close()
        except os.error as e:
            print('Could not install server as service: %s' %
                  e, '\nTry to run from superuser.')


def main():
    parser = argparse.ArgumentParser(
        description='PyTape Server 2020 Sakharuk Alexander')
    parser.add_argument('--host', action='store',
                        default='', help='Run on hostname [default is any host]')
    parser.add_argument('--port', action='store',
                        default=50077, help='Run on port [default is 50077]')
    parser.add_argument('--run', action='store_true', help='Run server')
    parser.add_argument('--install', action='store_true',
                        help='Install server as systemd daemon')
    args = parser.parse_args()

    server = Server(args.host, args.port)

    if(args.run):
        server.run()
    elif(args.install):
        server.install()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
