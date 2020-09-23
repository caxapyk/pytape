#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import asyncio
import argparse
import datetime
import os
import re
import smtplib
import socket
import subprocess
import sys
import time

conf = {
    'backup_dir': '/srv/nfs4/tape',
    'host': '',
    'port': 50077,
    'tape': '/dev/nst0',
    'mail_smtp_host': 'smtp.mail.ru',
    'mail_smtp_port': '465',
    'mail_from': 'proxima@gaorel.ru',
    'mail_to': 'sakharuk@gaorel.ru'
}


class Server():
    def __init__(self):
        self.__commands = {
            b'BACKUP': '_c_backup',
            b'BACKWARD': '_c_backward',
            b'CONFIG': '_c_config',
            b'HELLO': '_c_hello',
            b'EJECT': '_c_eject',
            b'ERASE': '_c_erase',
            b'LASTERR': '_c_lasterr',
            b'LIST': '_c_list',
            b'RECORD': '_c_record',
            b'REWIND': '_c_rewind',
            b'STATUS': '_c_status',
            b'TOWARD': '_c_toward',
            b'WIND': '_c_wind'
        }

        self.__smtp_pass = "e=KX30dujWnH"

        self.__last_error = b''

    async def run(self):
        try:
            server = await asyncio.start_server(
                self.handle_command, conf['host'], conf['port'])

            addr = server.sockets[0].getsockname()
            print(f'Serving on {addr}')

            # set TAPE env
            os.environ["TAPE"] = conf['tape']

            async with server:
                await server.serve_forever()
        except socket.error as e:
            print("Failed to start server. Error: %s" % e)
            sys.exit()

    async def handle_command(self, reader, writer):
        data = await reader.read(1024)
        addr = writer.get_extra_info('peername')

        print(f"Received {data!r} from {addr!r}")

        args = data.split()
        result = b''

        if args[0] in self.__commands:
            # run command handler
            result = await getattr(self, self.__commands[args[0]])(args)
        else:
            result = b'Server could not recognize command.'

        writer.write(result.encode())
        await writer.drain()

        writer.close()

    async def _execute(self, cmd):
        try:
            proc = subprocess.Popen(cmd, shell=True,
                                    stderr=subprocess.PIPE,
                                    stdout=subprocess.PIPE)
            if proc:
                stdout = proc.stdout.read()
                stderr = proc.stderr.read()

                return stdout, stderr

        except OSError as e:
            err = 'Could not start subprocess on server. Error: %s' % e
            print(str(err))

            return '', err

    #
    # Command handlers
    #

    async def _c_eject(self, args):
        x = 'mt eject'
        stdout, stderr = await self._execute(x)

        if stderr:
            self.__last_error = stderr.decode()
            return 'Could not eject the tape.'

        return 'Tape has been ejected.'

    async def _c_erase(self, args):
        x = 'mt erase'
        stdout, stderr = await self._execute(x)

        if stderr:
            self.__last_error = stderr.decode()
            return 'Could not earse the tape.'

        return 'Tape has been erased.'

    async def _c_backup(self, args):
        path = conf['backup_dir']
        if len(args) > 1:
            path = args[1].decode()

        start_time = time.time()

        x = 'mt eom && tar czv -C "$(dirname {})" $(basename {}) && (mt bsf 2 && mt fsf)'.format(
            path, path)
        stdout, stderr = await self._execute(x)

        if stderr:
            self.__last_error = stderr.decode()
            return 'Could not make backup.'

        complete_time = time.time()
        completed_dt = datetime.datetime.fromtimestamp(complete_time)
        completed_human = f"{completed_dt:%Y-%m-%d %H:%M:%S}"
        total_time = round((complete_time - start_time), 2)

        time_metrics = 'sec'
        if total_time / 60 > 1:
            time_metrics = 'min'

        # send email when backup done
        content = "Backup completed in {total}{metrics}.\nPath: {path}\nComplete time: {complete}".format(
            total=total_time,
            metrics=time_metrics,
            path=path,
            complete=completed_human)

        self.sendmail(content, 'Backup competed')

        return 'Backup competed.'

    async def _c_backward(self, args):
        count = args[1].decode()
        x = 'mt bsf $(({}+1)) && mt fsf'.format(count)
        stdout, stderr = await self._execute(x)

        if stderr:
            if "rmtopen" in str(stderr):
                self.__last_error = stderr.decode()
                return 'Could not go backward.'
            return 'Beginning of the tape has been reached.'

        return 'Rewinded on {} record(s)'.format(count)

    async def _c_config(self, args):
        _conf_ = "\n".join("{} = {}".format(c[0], c[1]) for c in conf.items())
        return _conf_

    async def _c_hello(self, args):
        return 'HELLO'

    async def _c_lasterr(self, args):
        return self.__last_error

    async def _c_list(self, args):
        x = 'tar tzv && mt bsf 2 && mt fsf'
        stdout, stderr = await self._execute(x)

        if stdout and stderr:
            return stdout.decode()
        elif not stdout and stderr:
            self.__last_error = stderr.decode()
            return 'Could not read a record. Probably on the border of the end.'
        elif not stdout and not stderr:
            return 'Record is empty.'

        return stdout.decode()

    async def _c_record(self, args):
        x = 'mt status | grep -e "file number = "'
        stdout, stderr = await self._execute(x)

        if stdout:
            return stdout.decode().replace('file', 'record')

        if stderr:
            self.__last_error = stderr.decode()
            return 'Could not get record number.'

    async def _c_rewind(self, args):
        x = 'mt rewind'
        stdout, stderr = await self._execute(x)

        if stderr:
            self.__last_error = stderr.decode()
            return 'Could not rewind the tape.'

        return 'Tape has been rewinded to beginning.'

    async def _c_status(self, args):
        x = 'mt status'
        stdout, stderr = await self._execute(x)

        if stderr:
            self.__last_error = stderr.decode()
            return 'Could not recieve status of the tape.'

        return stdout.decode()

    async def _c_toward(self, args):
        count = args[1].decode()
        x = 'mt fsf {}'.format(count)
        stdout, stderr = await self._execute(x)

        if stderr:
            if "rmtopen" in str(stderr):
                self.__last_error = stderr.decode()
                return 'Could not go toward.'

            return 'End of the tape has been reached.'

        return 'Winded on {} record(s)'.format(count)

    async def _c_wind(self, args):
        x = 'mt eom && mt bsf 2 && mt fsf'
        stdout, stderr = await self._execute(x)

        if stderr:
            self.__last_error = stderr.decode()
            return 'Could not rwind the tape.'

        return 'Tape has been rewinded to the end.'

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

    def sendmail(self, content, subject=''):
        try:
            message = 'Subject: {}\n\n{}'.format(subject, content)
            with smtplib.SMTP_SSL(
                conf['mail_smtp_host'], conf['mail_smtp_port']) as server:
                server.login(conf['mail_from'], self.__smtp_pass)
                server.sendmail(conf['mail_from'], conf['mail_to'], message)
                server.quit()

        except Exception as e:
            print('Could not send email. Error: %s' % e)


def main():
    parser = argparse.ArgumentParser(
        description='PyTape Server 2020 Sakharuk Alexander')

    parser.add_argument('--install', action='store_true',
                        help='Install server as systemd daemon')
    args = parser.parse_args()

    server = Server()

    if args.install:
        server.install()
    else:
        asyncio.run(server.run())


if __name__ == "__main__":
    main()
