# -*- coding: utf-8 -*-

"""
An instance of the Logmatic logger. Wraps the Python logger and some other 3rd-P integrations.
"""

import datetime
import inspect
import logging
import os
import sys
from logging.handlers import TimedRotatingFileHandler
from typing import Union
import dotenv
from logmatic.utils import pather
from logmatic.utils.truncate import truncate

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class Logger:

    # Color definitions.
    RED = '\33[31m'
    GREEN = '\33[32m'
    YELLOW = '\33[33m'
    BLUE = '\33[34m'
    DEFAULT_COLOR = '\33[0m'

    # DEFAULTS
    DEFAULT_ENV_PATH = "logmatic.env"
    COLUMN_PADDING: int = 8  # Minimum width of column when writing to console.

    # Config parsing.
    TRUE_VALUES = ("1", "on", "true")
    FALSE_VALUES = ("0", "off", "false")
    NULL_VALUES = ("0", "none", "null")

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
        self.file_logger = None
        self.file_logging_map: dict = None
        self.use_color: bool = True
        self.human_mode: bool = False
        self.trace: bool = True
        self.max_message_size = 256
        self.max_truncated_elements = 3

        # Minimum log level to print the log.
        self.console_log_level = logging.INFO
        self.file_log_level = logging.INFO

        self._auto_initialize()
        self._load_config()

        # Create the root logging map.
        self.root_logging_map: dict = {
            logging.DEBUG: logging.debug,
            logging.INFO: logging.info,
            logging.WARNING: logging.warning,
            logging.ERROR: logging.error,
            logging.CRITICAL: logging.critical,
        }

    # ======================================================================================================================
    # Loading and Initialization
    # ======================================================================================================================

    @staticmethod
    def _generate_default_config() -> dict:
        """ This is the default config for the log. Generate this if no config exists. """
        data = {
            "file_logger": {
                "active": True,
                "path": "./logs/output.log"
            },
            "rotation": {
                "interval_unit": "d",
                "interval_value": 1,
                "backup_count": 30
            },
            "console_log_level": "INFO",
            "file_log_level": "INFO",
            "human_mode": False,
            "trace": True,
            "max_message_size": 256,
            "max_truncated_elements": 3
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

        interval_unit = data["rotation"]["interval_unit"]
        interval_value = data["rotation"]["interval_value"]
        backup_count = data["rotation"]["backup_count"]

        self.human_mode = data["human_mode"]
        self.trace = data["trace"]
        self.max_message_size = data["max_message_size"]
        self.max_truncated_elements = data["max_truncated_elements"]

        if data["file_logger"]["active"]:
            self._attach_file_logger(data["file_logger"]["path"], interval_unit, interval_value, backup_count)

        # Set the appropriate log level.
        self.console_log_level = logging._nameToLevel[data["console_log_level"]]
        self.file_log_level = logging._nameToLevel[data["file_log_level"]]

        # Set the level of the native logger.
        self.file_logger.setLevel(self.file_log_level)
        self.file_logger.propagate = False
        if not self.human_mode:
            logging.basicConfig(
                level=self.console_log_level,
                stream=sys.stdout,
                format='%(levelname)s::%(asctime)s::%(message)s',
                datefmt="%Y-%m-%dT%H:%M:%S"
            )
            logging.info("Logmatic Initialized: Propagating logs to root logger and overriding root config.")

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
        self.set_file_logger(logging.getLogger("native_logger"))

    def _attach_file_logger(self, path, interval_unit: str = "d", interval_value: int = 1, backup_count: int = 30):
        pather.create(path)
        handler = TimedRotatingFileHandler(
            path,
            when=interval_unit,
            interval=interval_value,
            backupCount=backup_count)
        formatter = logging.Formatter(
            '%(levelname)s::%(asctime)s::%(message)s',
            datefmt="%Y-%m-%dT%H:%M:%S")
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

    def write(self, message, data, level, truncated: bool=True):

        # Parse the data first.
        data_string = None
        if data is not None:
            if type(data) is not dict:
                message = f"{message}: {str(data)}"
                data = None
            else:
                if truncated:
                    data_string = truncate(str(data), self.max_message_size)
                else:
                    data_string = str(data)

        module_trace = self.get_parent_module() if self.trace else None
        single_line_message = self.format_message_to_string(message, module_trace, data_string)
        file_logging_action = self.get_file_logging_action(level)
        if file_logging_action is not None:
            file_logging_action(single_line_message)

        if self.human_mode:
            self.console_write(message, module_trace, data, level, with_color=self.use_color, truncated=truncated)
        else:
            self.root_logging_map[level](single_line_message)

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

    def console_write(self, message, module_trace, data, level, with_color: bool = False, truncated: bool=False):
        """ Custom function to write message to console. """

        if level < self.console_log_level:
            return

        # Write the Header.
        self.console_write_line(message, module_trace, level, with_color)

        # Prepare the truncation limits.
        n_elements = 0

        # Write the Items.
        if data is not None:
            for k, v in data.items():
                if truncated and n_elements > self.max_truncated_elements:
                    self.console_write_line(f"  + {len(data) - n_elements} more elements...",
                                            module_trace, level, with_color)
                    break
                else:
                    n_elements += 1
                    use_key = k
                    if with_color:
                        use_key = self.set_level_color(k, level)
                    data_string = truncate(str(v), self.max_message_size) if truncated else str(v)
                    self.console_write_line(f"  {use_key}: {data_string}", module_trace, level, with_color)

    def console_write_line(self, content, module_trace, level, with_color: bool = False):
        time_str = f"{datetime.datetime.now():%H:%M}"
        module_str = "" if module_trace is None else f" {module_trace}"
        prefix = f"{logging.getLevelName(level)[:4]} {time_str}{module_str}"
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
