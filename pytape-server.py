#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import argparse
import os
import socket
import subprocess
import sys


class Server():
    def __init__(self):
        self.backup_dir = "/root"
        # protocol commands
        self.base_commands = {
            'STATUS': 'mt status',
            'LIST': 'tar tzv && mt bsf 2 && mt fsf',
            'BACKUP': 'mt eom && tar czv %s -C %s' % (self.get_bdir(), self.get_bdir()),
            'BACKUPSPECDIR': 'mt eom && tar czv {} -C {}',
            'REWIND': 'mt rewind'
        }

        self.ext_commands = {
            'GETBDIR': self.get_bdir(),
        }

    def run(self, host, port):
        # Create an AF_INET, STREAM socket (TCP)
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setblocking(True)
        except socket.error as e:
            print("Failed to create socket. Error: %s" % e)
            sys.exit()
        # Bind socket to local host and port
        try:
            sock.bind((host, port))
        except socket.error as e:
            print("Failed to bind socket. Error: %s" % e)
            sys.exit()
        # Start listening on socket
        sock.listen(1)
        print("Server started on %s:%s\n"
              "Waiting for client connections..." % (host, port))

        # Start main loop for waiting connections
        while True:
            conn, addr = sock.accept()
            print('Client connected by', addr)

            while True:
                data = conn.recv(1024)
                if not data:
                    break

                args = data.decode('utf-8').split()
                response = self._exec(args)

                conn.sendall(response)

        sock.close()

    def _exec(self, args):
        command = None

        if(args[0] in self.base_commands):
            if(len(args) > 1):
                command = self.base_commands[args[0]].format(*args[1::])
            else:
                command = self.base_commands[args[0]]

            try:
                proc = subprocess.Popen(command, shell=True,
                                        stderr=subprocess.PIPE,
                                        stdout=subprocess.PIPE)
                if proc:
                    out = proc.stdout.read()
                    stderr = proc.stderr.read()
                    if (stderr):
                        out += stderr
                    if(len(out) == 0):
                        out = b'Done'

                    return out
            except OSError as e:
                print('Could not start subprocess on server. Error: %s' % e)
                return b'Could not start subprocess on server.'

        elif(args[0] in self.ext_commands):
            return bytes(self.ext_commands[args[0]].encode("utf-8"))
        else:
            return b'Server could not recognize command.'

    def set_backup_dir(self, path):
        self.backup_dir = path

    def get_bdir(self):
        return self.backup_dir

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
            print('Could not install server as service. Error: %s' %
                  e, '\n\nTry to run from superuser.')


def main():
    parser = argparse.ArgumentParser(
        description='PyTape Server 2020 Sakharuk Alexander')
    parser.add_argument('--dir', action='store',
                        default='/root/',
                        help='Listen on interfaces [default is /root/]')
    parser.add_argument('--host', action='store',
                        default='',
                        help='Listen on interfaces [default is any]')
    parser.add_argument('--port', action='store',
                        default=50077,
                        help='Run on port [default is 50077]')
    parser.add_argument('--tape',
                        default='/dev/nst0',
                        help='Tape device [default is /dev/nst0]')
    parser.add_argument('--install', action='store_true',
                        help='Install server as systemd daemon')
    args = parser.parse_args()

    server = Server()
    server.set_backup_dir(args.dir)

    os.environ["TAPE"] = args.tape

    if(args.install):
        server.install()
    else:
        server.run(args.host, args.port)


if __name__ == "__main__":
    main()
