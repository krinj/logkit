# -*- coding: utf-8 -*-

"""
Static functions for using the logger. The logger is supposed to be set up
with lazy loading, and to be configured via the generated .env file.
"""

import logging
from typing import Union
from logmatic.logger import Logger

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


def debug(message, data=None, truncated: bool=False):
    __log_with_level(message, data, logging.DEBUG, truncated)


def info(message, data=None, truncated: bool=False):
    __log_with_level(message, data, logging.INFO, truncated)


def warning(message, data=None, truncated: bool=False):
    __log_with_level(message, data, logging.WARNING, truncated)


def error(message, data=None, truncated: bool=False):
    __log_with_level(message, data, logging.ERROR, truncated)


def critical(message, data=None, truncated: bool=False):
    __log_with_level(message, data, logging.CRITICAL, truncated)


def increment(metric_name: str, value: Union[float, int]=1):
    get_instance().increment(metric_name, value)


def gauge(metric_name: str, value: Union[float, int]):
    get_instance().gauge(metric_name, value)


def event(title: str, text: str, data: dict):
    get_instance().event(title, text, data)


def get_instance():
    return Logger.get_instance()


def __log_with_level(message, data, level, truncated):
    logger = Logger.get_instance()
    logger.write(message, data, level, truncated)
