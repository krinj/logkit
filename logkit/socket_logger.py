# -*- coding: utf-8 -*-

"""
This is a helper module that sends messages over a socket, if the socket is open and available.
If not, it will fail silently.
"""
import logging
import socket
import time


class SocketLogger:
    def __init__(self, host: str, port: int):

        # Back-off mechanism.
        self.current_backoff = 1
        self.prev_back_off_time = 0
        self.max_back_off = 64

        # Socket.
        socket.setdefaulttimeout(15)
        self.host = host
        self.port = port
        self.socket = None
        self.connect()

    def backoff(self):
        # Apply the back-off counter.
        self.current_backoff *= 2
        if self.current_backoff > self.max_back_off:
            self.current_backoff = self.max_back_off
        self.prev_back_off_time = time.time()

    def reset_backoff(self):
        # After a success, reset the current backoff back to 1.
        self.current_backoff = 1

    def is_backing_off(self):
        backoff_duration = time.time() - self.prev_back_off_time
        if backoff_duration > self.current_backoff:
            # It's no longer backing off.
            return False

        # It's still in the back-off phase.
        logging.warning("Socket backing off. Duration: {:.2f} - Limit: {}".format(
            backoff_duration,
            self.current_backoff
        ))
        return True

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            self.reset_backoff()
        except Exception as e:
            logging.error("Error: Unable to connect to socket: {}".format(str(e)))
            if self.socket is not None:
                self.socket.close()
                self.socket = None
            self.backoff()

    def close(self):
        try:
            self.socket.close()
        except Exception as e:
            logging.error("Warning: Unable to close socket: {}".format(str(e)))
        self.socket = None

    def send(self, message: str):

        if self.is_backing_off():
            return

        if self.socket is None:
            self.connect()

        if self.socket is not None:
            try:
                message += "\n"
                self.socket.sendall(bytes(message, "utf-8"))
                self.reset_backoff()
            except Exception as e:
                self.close()
                logging.error("Error: Unable to send socket message: {}".format(str(e)))
                self.backoff()
