# -*- coding: utf-8 -*-

from unittest import TestCase
from logmatic import log


class TestLogging(TestCase):
    def test_logging(self):

        log_functions = (log.debug, log.info, log.warning, log.error, log.critical)
        i = 0

        for f in log_functions:
            f(f"{i} Hello World")
            i += 1
            f(f"{i} Hello", "World")
            i += 1
            f(f"{i} Hello", {"target": "World"})
            i += 1

    def test_native_override(self):

        log_functions = (log.debug, log.info, log.warning, log.error, log.critical)
        i = 0

        for f in log_functions:
            f(f"{i} Hello World")
            i += 1
            f(f"{i} Hello", "World")
            i += 1
            f(f"{i} Hello", {"target": "World"})
            i += 1
