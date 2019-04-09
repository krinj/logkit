# -*- coding: utf-8 -*-
import logging
from unittest import TestCase
from logmatic import log


class TestLogging(TestCase):
    def test_logging(self):

        logging.warning("Hello World")

        log_functions = (log.debug, log.info, log.warning, log.error, log.critical)
        i = 0

        for f in log_functions:
            f(f"{i} Hello World")
            i += 1
            f(f"{i} Hello", "World")
            i += 1
            f(f"{i} Hello", {"target": "World"})
            i += 1
