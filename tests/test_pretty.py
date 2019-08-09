# -*- coding: utf-8 -*-
import datetime
import logging
import random
import uuid
from unittest import TestCase
from logkit import log


class TestLogging(TestCase):

    @staticmethod
    def write_time(delta):
        time_str = "{:%a, %d %b %H:%M}".format(datetime.datetime.now() + datetime.timedelta(minutes=delta))
        log.with_divider(time_str)

    def test_logging(self):

        print()

        # Log some normal information.
        log.info("Hello World!")

        # Add some arbitrary data.
        log.info("Some Data", {
            "counter": {"greetings": 5, "entry": 3},
            "schmeckles": [1, 2, 3],
            "lang": "EN"
        })

        self.write_time(20)

        # DEBUG: For extremely verbose things, that you will only need occasionally.
        log.info("User Login", {"id": uuid.uuid4().hex, "success": True, })
        log.warning("Please enforce 2FA for all accounts.")

        self.write_time(60)

        log.error("Unable to connect to Kafka server")
        log.error("Stream connection lost: ConnectionResetError(104)")

        print()
