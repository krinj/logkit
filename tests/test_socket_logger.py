# -*- coding: utf-8 -*-
import logging
import random
import time
from unittest import TestCase
from logkit import log


class TestSocketLogger(TestCase):
    def test_socket_logger(self):

        # Log some normal information.
        for i in range(100):
            log.info("Hello World", i)
            time.sleep(0.1)
