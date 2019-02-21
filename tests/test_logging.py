# -*- coding: utf-8 -*-
import logging
from unittest import TestCase
from logmatic import log


class TestLogging(TestCase):
    def test_logging(self):

        log.get_instance().level = logging.DEBUG
        log_functions = (log.debug, log.info, log.warning, log.error, log.critical)

        for f in log_functions:
            f("Hello World")
            f("Hello", "World")
            f("Hello", {"target": "World"})
