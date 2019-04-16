# -*- coding: utf-8 -*-

from unittest import TestCase
from logmatic import log


class TestLogging(TestCase):
    def test_logging(self):

        log_functions = (log.debug, log.info, log.warning, log.error, log.critical)
        i = 0

        busy_data = {}
        for j in range(1000):
            busy_data[f"key_{j}"] = j

        for f in log_functions:
            f(f"{i} Hello World")
            i += 1
            f(f"{i} Hello", "World")
            i += 1
            f(f"{i} Hello", {"target": "World"})
            i += 1
            f(f"{i} This message should be truncated", busy_data, truncated=True)
            i += 1
