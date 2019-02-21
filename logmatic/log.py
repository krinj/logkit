# -*- coding: utf-8 -*-

"""
<Description>
"""

import logging
from logmatic.logger import Logger

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


def debug(message, data=None):
    __log_with_level(message, data, logging.DEBUG)


def info(message, data=None):
    __log_with_level(message, data, logging.INFO)


def warning(message, data=None):
    __log_with_level(message, data, logging.WARNING)


def error(message, data=None):
    __log_with_level(message, data, logging.ERROR)


def critical(message, data=None):
    __log_with_level(message, data, logging.CRITICAL)


def get_instance():
    return Logger.get_instance()


def __log_with_level(message, data, level):
    logger = Logger.get_instance()
    logger.write(message, data, level)




