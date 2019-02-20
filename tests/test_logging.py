# -*- coding: utf-8 -*-

from unittest import TestCase
from logmatic import log


class TestLogging(TestCase):
    def test_logging(self):
        log.info("Hello World")
        log.info("Hello", "World")
        log.info("Hello", {"target": "World"})
        pass
