#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
A TCP Socket client to help test the socket logger.
"""

import socket


def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Socket binding.
    server_address = ('0.0.0.0', 5001)
    sock.bind(server_address)
    sock.listen(1)

    while True:
        print("Waiting for Connection...")
        connection, client_address = sock.accept()

        try:
            print("Connection from", client_address)

            # Receive the data in small chunks and retransmit it
            while True:
                data = connection.recv(2048)
                if data:
                    print("Received Data", {"data": str(data)})
                else:
                    print("No more data received.")
                    break

        finally:
            # Clean up the connection
            connection.close()


if __name__ == "__main__":
    main()

