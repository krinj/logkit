# -*- coding: utf-8 -*-
import logging
import time
from unittest import TestCase
from logmatic import log


class TestLogging(TestCase):
    def test_logging(self):

        log.get_instance().level = logging.DEBUG
        log_functions = (log.debug, log.info, log.warning, log.error, log.critical)

        i = 0

        for f in log_functions:
            f(f"{i} Hello World")
            i += 1
            f(f"{i} Hello", "World")
            i += 1
            f(f"{i} Hello", {"target": "World"})
            i += 1

    def test_datadog(self):

        # Increment Event
        for i in range(50):
            log.increment("logmatic.increment_test")
            time.sleep(0.05)

        for i in range(5):
            log.event("Testing Event", "Event Test Content", {"tag_name": "tag_detail", "index": i})
            time.sleep(0.05)
