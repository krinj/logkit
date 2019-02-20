# -*- coding: utf-8 -*-

"""
An instance of the Logmatic logger. Wraps the Python logger and some other integrations.
"""

import logging
from logging.handlers import TimedRotatingFileHandler

import yaml
from typing import List

from gv_tools.util import pather

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Logger:

    # Color definitions.
    RED = '\33[31m'
    GREEN = '\33[32m'
    YELLOW = '\33[33m'
    BLUE = '\33[34m'
    DEFAULT_COLOR = '\33[0m'

    # ======================================================================================================================
    # Singleton Access
    # ======================================================================================================================

    _instance = None

    @staticmethod
    def get_instance() -> "Logger":
        if Logger._instance is None:
            Logger._instance = Logger()
            Logger._instance.auto_initialize()
        return Logger._instance

    def __init__(self):
        # Native Python logging module.
        self.native_logger = None
        self.native_logging_map: dict = None
        self.auto_initialize()
        self._load_config()

    # ======================================================================================================================
    # Loading and Initialization
    # ======================================================================================================================

    def _load_config(self):
        with open("logmatic.yaml", "r") as f:
            data = yaml.load(f)
        print(data)
        print(data["file_logger"])
        if data["file_logger"]["active"]:
            self._attach_file_logger(data["file_logger"]["path"])

    def auto_initialize(self):
        self.set_native_logger(logging.getLogger("logger"))
        logging.basicConfig(level=logging.INFO)
        pass

    def _attach_json_logger(self):
        pass

    def _attach_file_logger(self, path):
        pather.create(path)
        handler = TimedRotatingFileHandler(
            path,
            when="m",
            interval=1,
            backupCount=5)
        self.native_logger.addHandler(handler)

    def set_native_logger(self, logger):
        # Log Level Map
        self.native_logger = logger
        self.native_logging_map = {
            logging.DEBUG: logger.debug,
            logging.INFO: logger.info,
            logging.WARNING: logger.warning,
            logging.ERROR: logger.error,
            logging.CRITICAL: logger.critical,
        } if logger is not None else {}

    # ======================================================================================================================
    # Third Party Attachments.
    # ======================================================================================================================

    # ...

    # ======================================================================================================================
    # Operational Logic
    # ======================================================================================================================

    def _get_native_logging_action(self, level):
        if self.native_logger is None:
            return None

        if level not in self.native_logging_map:
            return None

        return self.native_logging_map[level]

    def write(self, message, data, level):

        # Parse the data first.
        if data is not None:
            if type(data) is not dict:
                message = f"message: {str(data)}"
                data = None

        native_logging_action = self._get_native_logging_action(level)
        if native_logging_action is not None:
            native_logging_action(message, extra=data)
