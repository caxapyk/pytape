#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import argparse

from client import Client
from console import IConsole
from client_command import ClientCommand
from remote_command import RemoteCommand


def main():
    client = Client()

    parser = argparse.ArgumentParser(
        description='PyTape Client 2020 Sakharuk Alexander')
    parser.add_argument('-s', '--host', action='store', help='Server hostname')
    parser.add_argument('-p', '--port', action='store',
                        default=client.port(), help='Server port')

    args = parser.parse_args()

    if(args.host):
        client.connect(args.host, int(args.port))

    iconsole = IConsole()

    # Main loop
    while True:
        command = iconsole.run()
        if isinstance(command, ClientCommand):
            client._exec(command)
        elif isinstance(command, RemoteCommand):
            client.send(command)


if __name__ == "__main__":
    main()
