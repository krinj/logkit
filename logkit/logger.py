# -*- coding: utf-8 -*-

"""
An instance of the Logkit logger. Wraps the Python logger and some other 3rd-P integrations.
"""

import datetime
import inspect
import json
import logging
import os
import sys
import time
from logging.handlers import TimedRotatingFileHandler
from typing import Union
import shutil

import dotenv

from logkit.socket_logger import SocketLogger
from logkit.utils import pather
from logkit.utils.truncate import truncate

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Logger:

    # Color definitions.
    BLACK = '\33[90m'
    RED = '\33[31m'
    GREEN = '\33[32m'
    YELLOW = '\33[33m'
    BLUE = '\33[34m'
    PURPLE = '\33[35m'
    DEFAULT_COLOR = '\33[0m'

    # DEFAULTS
    DEFAULT_ENV_PATH = "logkit.env"
    COLUMN_PADDING: int = 2  # Minimum width of column when writing to console.

    # Config parsing.
    TRUE_VALUES = ("1", "on", "true")
    FALSE_VALUES = ("0", "off", "false")
    NULL_VALUES = ("0", "none", "null")

    ISO_TIME_FMT = "%Y-%m-%dT%H:%M:%S%z"
    LOG_FMT = "%(levelname)s::%(asctime)s::%(message)s"

    BOX_STEM = "├─"
    BOX_STEM_END = "└─"
    LOG_BULLET = "┃"
    H_BAR = "─"
    H_BAR_BULLET = "┠"
    TIME_BAR_INTERVAL = 60  # A minute between each bar print.

    # ======================================================================================================================
    # Singleton Access
    # ======================================================================================================================

    _instance = None

    @staticmethod
    def get_instance() -> "Logger":
        if Logger._instance is None:
            Logger._instance = Logger()
        return Logger._instance

    def __init__(self):
        # Native Python logging module.
        self.file_logger = None
        self.file_logging_map: dict = None

        self.socket_logger: SocketLogger = None

        self.with_color: bool = True
        self.with_level_prefix: bool = True
        self.human_mode: bool = False

        self.max_message_size = 256
        self.max_truncated_elements = 3

        # Minimum log level to print the log.
        self.console_log_level = logging.INFO
        self.file_log_level = logging.INFO

        self.native_logger = logging.getLogger('logkit')

        # Time bar management.
        self.last_bar_time = 0

        self._load_config()

        # Create the native logging map.
        self.native_logging_map: dict = {
            logging.DEBUG: self.native_logger.debug,
            logging.INFO: self.native_logger.info,
            logging.WARNING: self.native_logger.warning,
            logging.ERROR: self.native_logger.error,
            logging.CRITICAL: self.native_logger.critical,
        }

    # ======================================================================================================================
    # Loading and Initialization
    # ======================================================================================================================

    @staticmethod
    def _generate_default_config() -> dict:
        """ This is the default config for the log. Generate this if no config exists. """
        data = {

            "#1": "\n# If we should automatically write logs to disk.",
            "file_logger": {
                "active": False,
                "path": "./logs/output.log"
            },

            "#2": "\n# Settings for rotating the disk logs.",
            "rotation": {
                "interval_unit": "d",
                "interval_value": 1,
                "backup_count": 30
            },

            "#3": "\n# If we should automatically log to a socket.",
            "socket_logger": {
                "active": False,
                "host": "127.0.0.1",
                "port": 5000
            },

            "#4": "\n# Log levels to display [DEBUG, INFO, WARNING, ERROR, CRITICAL]",
            "console_log_level": "INFO",
            "file_log_level": "INFO",

            "#5": "\n# Readability settings for the console log.",
            "human_mode": True,
            "with_color": True,
            "with_level_prefix": False
        }
        return data

    def _append_to_env(self, key: str, value):
        with open(self.DEFAULT_ENV_PATH, "a") as f:
            f.write(f"\n{key}={value}")

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

        # Check for missing keys and add it to the .env.
        for k, v in data.items():

            if "#" in k:
                continue

            if type(v) is dict:

                for k2, v2 in v.items():
                    env_key = f"{k.upper()}__{k2.upper()}"

                    if env_key not in os.environ:
                        self._append_to_env(env_key, str(v2))
                        continue

                    if type(v2) is bool:
                        data[k][k2] = True if os.environ[env_key].lower() in self.TRUE_VALUES else False
                        continue

                    if type(v2) is int:
                        data[k][k2] = int(os.environ[env_key])
                        continue

                    data[k][k2] = None if os.environ[env_key].lower() in self.NULL_VALUES else str(os.environ[env_key])
            else:
                env_key = f"{k.upper()}"

                if env_key not in os.environ:
                    self._append_to_env(env_key, str(v))
                    continue

                if type(v) is bool:
                    data[k] = True if os.environ[env_key].lower() in self.TRUE_VALUES else False
                    continue

                if type(v) is int:
                    data[k] = int(os.environ[env_key])
                    continue

                data[k] = None if os.environ[env_key].lower() in self.NULL_VALUES else str(os.environ[env_key])

        self.human_mode = data["human_mode"]
        self.with_color = data["with_color"]
        self.with_level_prefix = data["with_level_prefix"]

        # Set the appropriate log level.
        self.console_log_level = logging._nameToLevel[data["console_log_level"]]
        self.file_log_level = logging._nameToLevel[data["file_log_level"]]

        interval_unit = data["rotation"]["interval_unit"]
        interval_value = data["rotation"]["interval_value"]
        backup_count = data["rotation"]["backup_count"]

        if data["file_logger"]["active"]:
            self.set_file_logger(logging.getLogger("logkit_file_logger"))
            self._attach_file_logger(data["file_logger"]["path"], interval_unit, interval_value, backup_count)
            self.file_logger.setLevel(self.file_log_level)
            self.file_logger.propagate = False

        if data["socket_logger"]["active"]:
            self.socket_logger = SocketLogger(
                host=data["socket_logger"]["host"],
                port=data["socket_logger"]["port"]
            )

        # Set the level of the native logger.
        if not self.human_mode:
            self.native_logger.propagate = False
            self.native_logger.setLevel(self.console_log_level)
            handler = logging.StreamHandler(sys.stdout)
            handler.setLevel(self.console_log_level)
            formatter = logging.Formatter(
                fmt=self.LOG_FMT,
                datefmt=self.ISO_TIME_FMT
            )
            handler.setFormatter(formatter)
            self.native_logger.addHandler(handler)
            self.native_logger.info("LogKit Initialized: Propagating logs to root logger and overriding root config.")

    def _save_config_env(self, data):
        lines = []
        for k, v in data.items():

            if "#" in k:
                lines.append(v)
                continue

            if type(v) is dict:
                for k2, v2 in v.items():
                    if v2 is None:
                        v2 = 0
                    lines.append(f"{k.upper()}__{k2.upper()}={v2}")
            else:
                if v is None:
                    v = 0
                lines.append(f"{k.upper()}={v}")

        pather.create(self.DEFAULT_ENV_PATH)
        with open(self.DEFAULT_ENV_PATH, "w") as f:
            f.writelines("\n".join(lines))

    def _attach_file_logger(self, path, interval_unit: str = "d", interval_value: int = 1, backup_count: int = 30):
        pather.create(path)
        handler = TimedRotatingFileHandler(
            path,
            when=interval_unit,
            interval=interval_value,
            backupCount=backup_count)
        formatter = logging.Formatter(
            self.LOG_FMT,
            datefmt=self.ISO_TIME_FMT)
        handler.setFormatter(formatter)
        self.file_logger.addHandler(handler)

    def set_file_logger(self, logger):
        # Log Level Map
        self.file_logger = logger
        self.file_logger.setLevel(self.file_log_level)
        self.file_logging_map = {
            logging.DEBUG: logger.debug,
            logging.INFO: logger.info,
            logging.WARNING: logger.warning,
            logging.ERROR: logger.error,
            logging.CRITICAL: logger.critical,
        } if logger is not None else {}

    # ======================================================================================================================
    # Operational Logic
    # ======================================================================================================================

    def get_file_logging_action(self, level):
        if self.file_logger is None:
            return None

        if level not in self.file_logging_map:
            return None

        return self.file_logging_map[level]

    def increment(self, metric_name: str, value: Union[float, int]):
        self.write(f"Incrementing {metric_name}: {value}", None, logging.DEBUG)

    def gauge(self, metric_name: str, value: Union[float, int]):
        self.write(f"Gauging {metric_name}: {value}", None, logging.DEBUG)

    # ======================================================================================================================
    # Normal Logging.
    # ======================================================================================================================

    def write_time_bar(self):
        if time.time() - self.last_bar_time >= self.TIME_BAR_INTERVAL:
            time_str = f"{datetime.datetime.now():%a, %d %b %H:%M}"
            self.write_with_divider(time_str)
            self.last_bar_time = time.time()

    def write_with_divider(self, message):
        cols, rows = shutil.get_terminal_size(fallback=(80, 456))
        content_length = len(message) + 2
        half_size = (cols - content_length) // 2
        left_side = self.set_color(self.H_BAR_BULLET + self.H_BAR * (half_size - 1), self.BLACK)

        right_side = self.H_BAR * half_size
        if content_length % 2 != 0:
            right_side += self.H_BAR
        right_side = self.set_color(right_side, self.BLACK)
        message = self.set_color(message, self.BLACK)

        formatted_message = f"{left_side} {message} {right_side}"
        print(formatted_message)
        sys.stdout.flush()

    def write(self, message, data, level, truncated: bool=False):

        # Parse the data first.
        data_string = None
        if data is not None:
            if type(data) is not dict:
                message = f"{message}: {str(data)}"
                data = None
            else:
                data_string = json.dumps(data)

        module_trace = self.get_parent_module()
        single_line_message = self.format_message_to_string(message, module_trace, data_string)
        file_logging_action = self.get_file_logging_action(level)
        if file_logging_action is not None:
            file_logging_action(single_line_message)

        if self.socket_logger is not None:
            time_format = datetime.datetime.now(datetime.timezone.utc).strftime(self.ISO_TIME_FMT)
            log_level = logging.getLevelName(level).upper()
            socket_message = f"{log_level}::{time_format}::{single_line_message}"
            self.socket_logger.send(socket_message)

        if self.human_mode:
            # Only human readable messages are truncated.
            self.console_write(message, data, level, with_color=self.with_color, truncated=truncated)
        else:
            self.native_logging_map[level](single_line_message)

    @staticmethod
    def format_message_to_string(message, module_trace, data):

        strings = []

        if module_trace is not None:
            strings.append(module_trace)

        strings.append(message)

        if data is not None:
            strings.append(data)
        else:
            strings.append("{}")

        strings = map(str, strings)
        return "::".join(strings)

    @staticmethod
    def get_parent_module() -> str:
        from_stack = inspect.stack()[4]
        stack_module = inspect.getmodule(from_stack[0])
        module_name = stack_module.__name__.split(".")[-1]
        return f"{module_name}:{from_stack.lineno}"

    def console_write(self, message, data, level, with_color: bool = False, truncated: bool=False):
        """ Custom function to write message to console. """

        if level < self.console_log_level:
            return

        # Check and write the time bar.
        self.write_time_bar()

        # Write the Header.
        self.console_write_line(message, level, with_color)

        # Prepare the truncation limits.
        n_elements = 0

        # Write the Items.
        if data is not None:
            for k, v in data.items():
                if truncated and n_elements > self.max_truncated_elements:
                    self.console_write_line(f"  + {len(data) - n_elements} more elements...",
                                            level, with_color)
                    break
                else:
                    n_elements += 1
                    use_key = k
                    data_string = truncate(str(v), self.max_message_size) if truncated else str(v)
                    stem = self.BOX_STEM if n_elements < len(data) else self.BOX_STEM_END
                    if with_color:
                        use_key = self.set_level_color(k, level)
                        stem = self.set_level_color(stem, level)
                    self.console_write_line(f"  {stem} {use_key}: {data_string}",
                                            level, with_color)

    def console_write_line(self, content, level, with_color: bool = False):

        prefix = self.LOG_BULLET
        if self.with_level_prefix:
            prefix += f" {logging.getLevelName(level)[:4]}: "
        pad_length = max(0, self.COLUMN_PADDING - len(prefix))
        prefix += " " * pad_length

        if with_color:
            if level > logging.INFO:
                content = f"{prefix} {content}"
                content = self.set_level_color(content, level)
            else:
                prefix = self.set_level_color(prefix, level)
                content = f"{prefix} {content}"
        else:
            content = f"{prefix} {content}"

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
            return self.set_color(content, self.PURPLE)
        return content

    def set_color(self, content, color):
        return f"{color}{content}{self.DEFAULT_COLOR}"
