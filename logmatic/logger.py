# -*- coding: utf-8 -*-

"""
An instance of the Logmatic logger. Wraps the Python logger and some other integrations.
"""
import datetime
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
import yaml
from gv_tools.util import pather
from logmatic.formatter.extended_json_formatter import ExtendedJSONFormatter

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Logger:

    # Color definitions.
    RED = '\33[31m'
    GREEN = '\33[32m'
    YELLOW = '\33[33m'
    BLUE = '\33[34m'
    DEFAULT_COLOR = '\33[0m'

    DEFAULT_CONFIG_PATH = "logmatic.yaml"
    COLUMN_PADDING: int = 8  # Minimum width of column when writing to console.

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
        self.use_color: bool = True
        self.level = logging.INFO
        self.auto_initialize()
        self._load_config()

    # ======================================================================================================================
    # Loading and Initialization
    # ======================================================================================================================

    @staticmethod
    def _generate_default_config() -> dict:
        """ This is the default config for the log. Generate this if no config exists. """
        data = {
            "json_logger": {
                "active": True,
                "path": "./logs/output.json"
            },
            "file_logger": {
                "active": True,
                "path": "./logs/output.log"
            },
            "rotation": {
                "interval_unit": "m",
                "interval_value": 1
            }
        }
        return data

    def _load_config(self):
        """
        Attempt to load the logger config file.
        If none exists, we will create one first.
        This should only be used ONCE per logger, otherwise we over-add handlers.
        """

        if not os.path.exists(self.DEFAULT_CONFIG_PATH):
            # Create a new path.
            data = self._generate_default_config()
            with open(self.DEFAULT_CONFIG_PATH, "w") as f:
                yaml.dump(data, f, default_flow_style=False)

        with open(self.DEFAULT_CONFIG_PATH, "r") as f:
            data = yaml.load(f)

        if data["file_logger"]["active"]:
            self._attach_file_logger(data["file_logger"]["path"])

        if data["json_logger"]["active"]:
            self._attach_json_logger(data["json_logger"]["path"])

    def auto_initialize(self):
        self.set_native_logger(logging.getLogger("logger"))

    def _attach_json_logger(self, path, interval_unit: str="d", interval_value: int=1, backup_count: int =10):
        pather.create(path)
        handler = TimedRotatingFileHandler(
            path,
            when=interval_unit,
            interval=interval_value,
            backupCount=backup_count)
        formatter = ExtendedJSONFormatter()
        handler.setFormatter(formatter)
        self.native_logger.addHandler(handler)

    def _attach_file_logger(self, path, interval_unit: str="d", interval_value: int=1, backup_count: int =10):
        pather.create(path)
        handler = TimedRotatingFileHandler(
            path,
            when=interval_unit,
            interval=interval_value,
            backupCount=backup_count)
        formatter = logging.Formatter(
            "%(levelname)s:%(asctime)s | %(message)s | %(data)s",
            datefmt="%Y/%m/%d:%H:%M:%S")
        handler.setFormatter(formatter)
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
                message = f"{message}: {str(data)}"
                data = None

        native_logging_action = self._get_native_logging_action(level)
        if native_logging_action is not None:
            native_logging_action(message, extra={"data": data})

        self.console_write(message, data, level, with_color=self.use_color)

    def console_write(self, message, data, level, with_color: bool=False):
        """ Custom function to write message to console. """

        if level < self.level:
            return

        # Add Header
        self.console_write_line(message, level, with_color)

        if data is not None:
            for k, v in data.items():
                self.console_write_line(f"  {k}: {v}", level, with_color)

    def console_write_line(self, content, level, with_color: bool=False):
        time_str = f"{datetime.datetime.now():%H:%M}"
        prefix = f"{logging.getLevelName(level)[:4]} {time_str}"
        pad_length = max(0, self.COLUMN_PADDING - len(prefix))
        prefix += " " * pad_length
        if with_color:
            prefix = self.set_level_color(prefix, level)
        content = f"{prefix}  {content}"
        print(content)
        sys.stdout.flush()

    def set_level_color(self, content, level):
        if level == logging.INFO:
            return self.set_color(content, self.BLUE)
        if level == logging.DEBUG:
            return self.set_color(content, self.GREEN)
        if level == logging.WARNING:
            return self.set_color(content, self.YELLOW)
        if level == logging.ERROR:
            return self.set_color(content, self.RED)
        if level == logging.CRITICAL:
            return self.set_color(content, self.RED)
        return content

    def set_color(self, content, color):
        return f"{color}{content}{self.DEFAULT_COLOR}"
