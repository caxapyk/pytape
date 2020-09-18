#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import argparse

from client import Client


def main():
    parser = argparse.ArgumentParser(
        description='PyTape Client 2020 Sakharuk Alexander')
    parser.add_argument('-s', '--host', action='store',
                        default='localhost', help='Server hostname')
    parser.add_argument('-p', '--port', action='store',
                        default=50077, help='Server port')

    args = parser.parse_args()

    client = Client()
    client.connect(args.host, args.port)
    client.console()


if __name__ == "__main__":
    main()
