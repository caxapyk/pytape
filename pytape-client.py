#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import asyncio
import argparse

from client import Client


def main():
    parser = argparse.ArgumentParser(
        description='PyTape Client 2020 Sakharuk Alexander')

    parser.add_argument('-s', '--host', action='store', help='Server hostname')
    parser.add_argument('-p', '--port', default=50077,
                        action='store', help='Server port')

    args = parser.parse_args()

    client = Client()
    asyncio.run(client.run(args.host, args.port))


if __name__ == "__main__":
    main()
