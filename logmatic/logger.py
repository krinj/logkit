# -*- coding: utf-8 -*-

"""
An instance of the Logmatic logger. Wraps the Python logger and some other 3rd-P integrations.
"""

import datetime
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import Union

import dotenv
from logmatic.formatter.extended_json_formatter import ExtendedJSONFormatter
from logmatic.utils import pather

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Logger:
    # Color definitions.
    RED = '\33[31m'
    GREEN = '\33[32m'
    YELLOW = '\33[33m'
    BLUE = '\33[34m'
    DEFAULT_COLOR = '\33[0m'
    DEFAULT_ENV_PATH = "logmatic.env"
    COLUMN_PADDING: int = 8  # Minimum width of column when writing to console.

    # ======================================================================================================================
    # Singleton Access
    # ======================================================================================================================

    _instance = None

    @staticmethod
    def get_instance() -> "Logger":
        if Logger._instance is None:
            Logger._instance = Logger()
            Logger._instance._auto_initialize()
        return Logger._instance

    def __init__(self):
        # Native Python logging module.
        self.native_logger = None
        self.native_logging_map: dict = None
        self.use_color: bool = True
        self.print_gap: bool = True

        # Minimum log level to print the log.
        self.console_log_level = logging.INFO
        self.file_log_level = logging.INFO

        self._auto_initialize()
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
                "path": "./logs/output.json.log"
            },
            "file_logger": {
                "active": True,
                "path": "./logs/output.log"
            },
            "rotation": {
                "interval_unit": "d",
                "interval_value": 1,
                "backup_count": 30
            },
            "print_gap": 1,
            "console_log_level": "INFO",
            "file_log_level": "INFO"
        }
        return data

    def _load_config(self):
        """
        Attempt to load the logger config file.
        If none exists, we will create one first.
        This should only be used ONCE per logger, otherwise we over-add handlers.
        """

        data = self._generate_default_config()
        if not os.path.exists(self.DEFAULT_ENV_PATH):
            self._save_config_env(data)

        dotenv.load_dotenv(self.DEFAULT_ENV_PATH)
        for k, v in data.items():
            if type(v) is dict:

                for k2, v2 in v.items():
                    env_key = f"{k.upper()}__{k2.upper()}"

                    if type(v2) is bool:
                        data[k][k2] = True if os.environ[env_key] == "1" else False
                        continue

                    if type(v2) is int:
                        data[k][k2] = int(os.environ[env_key])
                        continue

                    data[k][k2] = None if os.environ[env_key] == "0" else str(os.environ[env_key])
            else:
                env_key = f"{k.upper()}"

                if type(v) is bool:
                    data[k] = True if os.environ[env_key] == "1" else False
                    continue

                if type(v) is int:
                    data[k] = int(os.environ[env_key])
                    continue

                data[k] = None if os.environ[env_key] == "0" else str(os.environ[env_key])

        interval_unit = data["rotation"]["interval_unit"]
        interval_value = data["rotation"]["interval_value"]
        backup_count = data["rotation"]["backup_count"]
        self.print_gap = data["print_gap"]

        if data["file_logger"]["active"]:
            self._attach_file_logger(data["file_logger"]["path"], interval_unit, interval_value, backup_count)

        if data["json_logger"]["active"]:
            self._attach_json_logger(data["json_logger"]["path"], interval_unit, interval_value, backup_count)

        # Set the appropriate log level.
        self.console_log_level = logging._nameToLevel[data["console_log_level"]]
        self.file_log_level = logging._nameToLevel[data["file_log_level"]]

    def _save_config_env(self, data):
        lines = []
        for k, v in data.items():
            if type(v) is dict:
                for k2, v2 in v.items():
                    if v2 is True:
                        v2 = 1
                    if v2 is False or v2 is None:
                        v2 = 0
                    lines.append(f"{k.upper()}__{k2.upper()}={v2}")
            else:
                if v is True:
                    v = 1
                if v is False or v is None:
                    v = 0
                lines.append(f"{k.upper()}={v}")

        pather.create(self.DEFAULT_ENV_PATH)
        with open(self.DEFAULT_ENV_PATH, "w") as f:
            f.writelines("\n".join(lines))

    def _auto_initialize(self):
        self.set_native_logger(logging.getLogger("logger"))

    def _attach_json_logger(self, path, interval_unit: str = "d", interval_value: int = 1, backup_count: int = 30):
        pather.create(path)
        handler = TimedRotatingFileHandler(
            path,
            when=interval_unit,
            interval=interval_value,
            backupCount=backup_count)
        formatter = ExtendedJSONFormatter()
        handler.setFormatter(formatter)
        self.native_logger.addHandler(handler)

    def _attach_file_logger(self, path, interval_unit: str = "d", interval_value: int = 1, backup_count: int = 30):
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
        self.native_logger.setLevel(self.file_log_level)
        self.native_logging_map = {
            logging.DEBUG: logger.debug,
            logging.INFO: logger.info,
            logging.WARNING: logger.warning,
            logging.ERROR: logger.error,
            logging.CRITICAL: logger.critical,
        } if logger is not None else {}

    # ======================================================================================================================
    # Operational Logic
    # ======================================================================================================================

    def _get_native_logging_action(self, level):
        if self.native_logger is None:
            return None

        if level not in self.native_logging_map:
            return None

        return self.native_logging_map[level]

    def event(self, title: str, text: str, data: dict):
        message = f"{title}: {text}"
        self.write(message, data, logging.INFO)

    def increment(self, metric_name: str, value: Union[float, int]):
        self.write(f"Incrementing {metric_name}: {value}", None, logging.DEBUG)

    def gauge(self, metric_name: str, value: Union[float, int]):
        self.write(f"Gauging {metric_name}: {value}", None, logging.DEBUG)

    # ======================================================================================================================
    # Normal Logging.
    # ======================================================================================================================

    def write(self, message, data, level, is_internal: bool=False):

        # Parse the data first.
        if data is not None:
            if type(data) is not dict:
                message = f"{message}: {str(data)}"
                data = None

        native_logging_action = self._get_native_logging_action(level)
        if native_logging_action is not None:
            native_logging_action(message, extra={"data": data})

        self.console_write(message, data, level, with_color=self.use_color)

    def console_write(self, message, data, level, with_color: bool = False):
        """ Custom function to write message to console. """

        if level < self.console_log_level:
            return

        # Add a gap if we are printing a dict.
        if self.print_gap:
            print()

        # Write the Header.
        self.console_write_line(message, level, with_color)

        # Write the Items.
        if data is not None:
            for k, v in data.items():
                use_key = k
                if with_color:
                    use_key = self.set_level_color(k, level)
                self.console_write_line(f"  {use_key}: {v}", level, with_color)

    def console_write_line(self, content, level, with_color: bool = False):
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
