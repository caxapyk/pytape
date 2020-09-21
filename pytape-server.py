#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import asyncio
import argparse
import os
import re
import socket
import subprocess
import sys

conf = {
    'backup_dir': '/root',
    'host': '',
    'port': 50077,
    'tape': '/dev/nst0'
}


class Server():
    def __init__(self):
        self.__commands = {
            b'BACKUP': '_c_backup',
            b'BACKWARD': '_c_backward',
            b'CONFIG': '_c_config',
            b'ERASE': '_c_erase',
            b'LIST': '_c_list',
            b'REWIND': '_c_rewind',
            b'STATUS': '_c_status',
            b'TOWARD': '_c_toward',
            b'WIND': '_c_wind'
        }

    async def handle_command(self, reader, writer):
        data = await reader.read(1024)
        addr = writer.get_extra_info('peername')

        print(f"Received {data!r} from {addr!r}")

        result = b''

        # echo b'HELLO' command
        if(data == b'HELLO'):
            result = data
        else:
            args = data.split()

            if args[0] in self.__commands:
                # run command handler
                result = await getattr(self, self.__commands[data])(args)
            else:
                result = b'Server could not recognize command.'

        writer.write(result)
        await writer.drain()

        writer.close()

    # async def run(self, host, port):
        # Create an AF_INET, STREAM socket (TCP)
        # try:
        #    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #    sock.setblocking(True)
        # except socket.error as e:
        #    print("Failed to create socket. Error: %s" % e)
        #    sys.exit()
        # Bind socket to local host and port
        # try:
        #    sock.bind((host, port))
        # except socket.error as e:
        #    print("Failed to bind socket. Error: %s" % e)
        #    sys.exit()
        # Start listening on socket
        # sock.listen(1)
        # print("Server started on %s:%s\n"
        #      "Waiting for client connections..." % (host, port))

        # Start main loop for waiting connections
        # while True:
        #    conn, addr = sock.accept()
        #    print('Client connected by', addr)

        #    while True:
        #        data = conn.recv(1024)
        #        if not data:
        #            break

        # args = data.decode('utf-8').split()
        #        args = data.split()
        #        response = self._exec(args)

        #        conn.sendall(response)

        # sock.close()

    # def _exec(self, args):
    #    if args[0] in self.__commands:
    #        # run command handler
    #        return getattr(self, self.__commands[args[0]])(args)
    #    else:
    #        return b'Server could not recognize command.'

    def _shell(self, command):
        try:
            proc = subprocess.Popen(command, shell=True,
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            if proc:
                stdout = proc.stdout.read()
                stderr = proc.stderr.read()

                return stdout, stderr

        except OSError as e:
            err = bytes(
                'Could not start subprocess on server. Error: %s' % e, 'utf-8')

            print(str(err))

            return '', err

    #
    # Command handlers
    #

    async def _c_erase(self, args):
        x = 'mt erase'
        stdout, stderr = self._shell(x)

        return stdout + stderr

    async def _c_backup(self, args):
        x = 'mt eom && tar czv {} -C {}'.format(
            conf['backup_dir'], conf['backup_dir'])
        stdout, stderr = self._shell(x)

        return stdout + stderr

    async def _c_backward(self, args):
        x = 'mt bsf $(({}+1)) && mt fsf'.format(args[1].decode('utf-8'))
        stdout, stderr = self._shell(x)

        return stdout + stderr

    async def _c_config(self, args):
        return bytes(str(conf), 'utf-8')

    async def _c_list(self, args):
        x = 'tar tzv && mt bsf 2 && mt fsf'
        stdout, stderr = self._shell(x)

        return stdout + stderr

    async def _c_rewind(self, args):
        x = 'mt rewind'
        stdout, stderr = self._shell(x)

        return stdout + stderr

    async def _c_status(self, args):
        x = 'mt status'
        stdout, stderr = self._shell(x)

        return stdout + stderr

    async def _c_toward(self, args):
        x = 'mt fsf {}'.format(args[1].decode('utf-8'))
        stdout, stderr = self._shell(x)

        return stdout + stderr

    async def _c_wind(self, args):
        x = 'mt eom && mt bsf 2 && mt fsf'
        stdout, stderr = self._shell(x)

        return stdout + stderr

    #
    # Systemd Installer
    #

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


async def main():
    parser = argparse.ArgumentParser(
        description='PyTape Server 2020 Sakharuk Alexander')

    parser.add_argument('--install', action='store_true',
                        help='Install server as systemd daemon')
    args = parser.parse_args()

    server = Server()

    if args.install:
        server.install()
    else:
        server = await asyncio.start_server(
            server.handle_command, conf['host'], conf['port'])

        addr = server.sockets[0].getsockname()
        print(f'Serving on {addr}')

        # set TAPE env
        os.environ["TAPE"] = conf['tape']

        async with server:
            await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())
