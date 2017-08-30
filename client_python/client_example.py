# -*- coding: utf-8 -*-
#
# example python client code for smart vehicle security system
#

import socket
import sys


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    host = socket.gethostbyname('localhost')
    port = 2200

    # connection to hostname on the port.
    sock.connect((host, port))
    print('Connected to server...')
    data = sock.recv(1024)
    print('Recieved: ' + data.decode())
    to_send = raw_input('Data: ')
    while True:
        to_send = to_send.upper().encode()
        sock.sendall(to_send)
        data = sock.recv(1024)
        print('Recieved: ' + data.decode())
        to_send = raw_input('Data: ')

if __name__ == '__main__':
    main()
