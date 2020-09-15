#
# PyTape 2020 Sakharuk Alexander <saharuk.alexander@gmail.com>
# Licensed by GNU GENERAL PUBLIC LICENSE Version 3
#

import argparse
import socket


class Client():
    def connect(self, host, port):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.connect((host, port))
            sock.sendall(b'STATUSTAPE /dev/tape0')

            data = sock.recv(2048)
            print('Received', data.decode('utf-8'))
            sock.close()

        except socket.error as e:
            sock.close()
            print('Connection error: %s' % e)


def main():
    parser = argparse.ArgumentParser(
        description='PyTape Client 2020 Сахарук Александр')
    parser.add_argument('-s', '--server', action='store',
                        default='localhost', help='Адрес сервера')
    parser.add_argument('-p', '--port', action='store',
                        default=50077, help='Порт сервера')
    args = parser.parse_args()

    client = Client()
    client.connect(args.server, args.port)


if __name__ == "__main__":
    main()
