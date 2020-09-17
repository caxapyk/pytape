#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import argparse
import os
import socket
import subprocess
import sys

conf = {
    'backup_dir': '/root',
    'host': '',
    'port': 50077,
    'tape': '/dev/nst0'
}

ERR_CODE = b'0x01'


class Server():
    def __init__(self):
        self.last_err = b' '
        # protocol commands
        self.com = {
            'BACKUP': ('shell', 'mt eom && tar czv %s -C %s' %
                       (conf['backup_dir'], conf['backup_dir'])),
            'BACKUPSPECDIR': ('shell', 'mt eom && tar czv {} -C {}'),
            'BACKWARD': ('shell', 'mt bsf $(({}+1)) && mt fsf'),
            'ERASE': ('shell', 'mt erase'),
            'GETBDIR': ('value', bytes(conf['backup_dir'], 'utf-8')),
            'LASTERR': ('funct', 'get_last_err'),
            'LIST': ('shell', 'tar tzv && mt bsf 2 && mt fsf'),
            'REWIND': ('shell', 'mt rewind'),
            'STATUS': ('shell', 'mt status'),
            'TOWARD': ('shell', 'mt fsf {}'),
            'WIND': ('shell', 'mt eom && mt bsf 2 && mt fsf'),
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

    def get_last_err(self):
        return self.last_err

    def _exec(self, args):
        if(args[0] in self.com):
            # command type
            c_type = self.com[args[0]][0]
            # command value
            c_val = self.com[args[0]][1]

            if(c_type == "shell" and len(args) == 1):
                return self._shell(c_val)
            elif(c_type == "shell" and len(args) > 1):
                print(c_val.format(*args[1::]))
                return self._shell(c_val.format(*args[1::]))
            elif(c_type == "value"):
                return c_val
            elif(c_type == "funct"):
                return getattr(self, c_val)()
        else:
            self.last_err = b'Server could not recognize command.'

            return ERR_CODE

    def _shell(self, command):
        try:
            proc = subprocess.Popen(command, shell=True,
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            if proc:
                out = proc.stdout.read()
                err = proc.stderr.read()

                if(len(out) == 0 and len(err) == 0):
                    out = b' '
                elif(len(out) == 0 and len(err) > 0):
                    self.last_err = err
                    return ERR_CODE

                return out

        except OSError as e:
            self.last_err = bytes(
                'Could not start subprocess on server. Error: %s' % e, 'utf-8')

            print(str(self.last_err))

            return ERR_CODE

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
            sys.exit()


def main():
    parser = argparse.ArgumentParser(
        description='PyTape Server 2020 Sakharuk Alexander')

    parser.add_argument('--install', action='store_true',
                        help='Install server as systemd daemon')
    args = parser.parse_args()

    server = Server()
    os.environ["TAPE"] = conf['tape']

    if(args.install):
        server.install()
    else:
        server.run(conf['host'], conf['port'])


if __name__ == "__main__":
    main()
