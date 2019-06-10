# -*- coding: utf-8 -*-

"""
Static functions for using the logger. The logger is supposed to be set up
with lazy loading, and to be configured via the generated .env file.
"""

import threading
import time
from typing import Union, Dict
from .log import info

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


DEFAULT_PULSE_KEY = "default"
PULSE_MAP = {}


class Pulse:

    SECONDS = "s"
    MINUTES = "m"
    HOURS = "h"
    HEART = "❤"  # f"\33[31m❤\33[0m"
    SLEEP_INTERVAL = 1

    def __init__(self, key: str, interval_unit: str="m", interval_value: int=15):

        # Initialize an instance of a Pulse.
        self.key = key

        # Set the interval.
        self.interval_unit = None
        self.interval_value = None
        self._interval = None
        self.set_interval(interval_unit, interval_value)

        # Internal Meta-data.
        self._time_start_str = self._get_time_str()
        self._time_end_str = self._get_time_str()
        self._prev_time = time.time()

        # History of counter and gauges.
        self.counter_map = {}
        self.gauge_map = {}

        info("Pulse Initialized", {"key": key})

        # Start the event loop.
        threading.Thread(target=self._loop, daemon=True).start()

    def set_interval(self, interval_unit: str, interval_value: int):
        self.interval_unit = interval_unit
        self.interval_value = interval_value

        # Calculate interval factor.
        if self.interval_unit == self.MINUTES:
            interval_factor = 60
        elif self.interval_unit == self.HOURS:
            interval_factor = 60 * 60
        else:
            interval_factor = 1
        self._interval = self.interval_value * interval_factor

        info("Pulse Interval Set", {
            "interval": self._interval,
            "interval_units": self.interval_unit,
            "interval_value": self.interval_value
        })

    def increment(self, key: str, delta: Union[float, int]=1):
        if key not in self.counter_map:
            self.counter_map[key] = delta
        else:
            self.counter_map[key] += delta
    
    def gauge(self, key: str, value: Union[float, int]):
        self.gauge_map[key] = value

    def _loop(self):
        while True:
            time.sleep(self.SLEEP_INTERVAL)
            duration = time.time() - self._prev_time
            if duration > self._interval:
                self._execute()

    def _execute(self):
        # The interval has come, so we can send the messages.
        counter_data = {}
        gauge_data = {}

        self._time_end_str = self._get_time_str()

        for k, v in self.counter_map.items():
            counter_data[k] = v
            self.counter_map[k] = 0

        for k, v in self.gauge_map.items():
            gauge_data[k] = v
            self.gauge_map[k] = 0

        info("{} Pulse {}".format(self.HEART, self.HEART), {
            "t_from": self._time_start_str,
            "t_stop": self._time_end_str,
            "counter": counter_data,
            "gauge": gauge_data,
        })

        # Reset all parameters.
        self._time_start_str = self._get_time_str()
        self._prev_time = time.time()

    @staticmethod
    def _get_time_str():
        return time.strftime('%d %b %H:%M')


def get(key: str="default"):
    if key not in PULSE_MAP:
        PULSE_MAP[key] = Pulse(key)
    return PULSE_MAP[key]


def set_interval(interval_unit: str, interval_value: int):
    pulse = get(DEFAULT_PULSE_KEY)
    pulse.set_interval(interval_unit, interval_value)


def increment(key: str, delta: Union[float, int]=1):
    pulse = get(DEFAULT_PULSE_KEY)
    pulse.increment(key, delta)


def gauge(key: str, value: Union[float, int]=1):
    pulse = get(DEFAULT_PULSE_KEY)
    pulse.gauge(key, value)
