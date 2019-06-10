# -*- coding: utf-8 -*-

import time
from unittest import TestCase
from logkit import pulse


class TestLogging(TestCase):
    def test_pulse(self):
        print("Testing Pulse")
        pulse.increment("detections", 5)
        pulse.increment("detections", 5)
        pulse.increment("detections", 5)
        pulse.increment("detections", 5)
        time.sleep(5)
