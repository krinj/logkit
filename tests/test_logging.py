# -*- coding: utf-8 -*-
import logging
import random
from unittest import TestCase
from logmatic import log


class TestLogging(TestCase):
    def test_logging(self):

        print()

        log.with_divider("This is a divider!")
        log.with_divider("A")
        log.with_divider("AA")
        log.with_divider("AAA")

        # Log some normal information.
        log.info("Hello World!")

        # Add some arbitrary data.
        log.info("Some Data", {"greeting_count": 1, "schmeckles": [1, 2, 3], "lang": "EN"})

        # DEBUG: For extremely verbose things, that you will only need occasionally.
        log.debug("My left stroke just went viral.")

        # WARNING: For things that aren't breaking, but should be avoided.
        log.warning("Be careful!")

        # ERROR: Things that are breaking and need to be fixed.
        log.error("This is an error.")

        # CRITICAL: This is for something major that will cause a system failure.
        log.critical("OMG. We are on fire.")

        print()

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
