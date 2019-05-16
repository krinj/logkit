# -*- coding: utf-8 -*-

"""
This is a helper module that sends messages over a socket, if the socket is open and available.
If not, it will fail silently.
"""
import logging
import socket


class SocketLogger:
    def __init__(self, host: str, port: int):
        self.host: str = host
        self.port: int = port
        self.socket = None
        self.connect()

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
        except Exception as e:
            logging.debug(f"Error: Unable to connect to socket: {e}")
            self.socket.close()
            self.socket = None

    def close(self):
        try:
            self.socket.close()
        except Exception as e:
            logging.debug(f"Warning: Unable to close socket: {e}")
        self.socket = None

    def send(self, message: str):
        if self.socket is None:
            self.connect()
        try:
            message += "\n"
            self.socket.sendall(bytes(message, "utf-8"))
        except Exception as e:
            self.close()
            logging.debug(f"Error: Unable to send socket message: {e}")
