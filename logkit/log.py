# -*- coding: utf-8 -*-

"""
Static functions for using the logger. The logger is supposed to be set up
with lazy loading, and to be configured via the generated .env file.
"""

import logging
from logkit.logger import Logger

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


def with_divider(message):
    logger = Logger.get_instance()
    logger.write_with_divider(message)


def get_instance():
    return Logger.get_instance()


def __log_with_level(message, data, level, truncated):
    logger = Logger.get_instance()
    logger.write(message, data, level, truncated)
