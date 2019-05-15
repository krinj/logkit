# -*- coding: utf-8 -*-
import logging
import random
from unittest import TestCase
from logmatic import log


class TestLogging(TestCase):
    def test_logging(self):

        logging.warning("This is a native logging output.")
        print("This is a native print output.")

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
            f(f"{i} Payload", {"rooples": i, "schmeckles": [1, 2, 3], "rand": random.random()})
            i += 1

        logging.warning("This is another native logging output.")
