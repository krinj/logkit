# -*- coding: utf-8 -*-

"""
<Description>
"""

import logging
from typing import Union

from logmatic.logger import Logger

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


def debug():
    pass


def info(message, data=None):
    __log_with_level(message, data, logging.INFO)


def warn():
    pass


def error():
    pass


def critical():
    pass


def __log_with_level(message, data, level):
    logger = Logger.get_instance()
    logger.write(message, data, level)




