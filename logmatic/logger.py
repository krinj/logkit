# -*- coding: utf-8 -*-

"""
An instance of the Logmatic logger. Wraps the Python logger and some other 3rd-P integrations.
"""

import datetime
import json
import logging
import os
import sys
import threading
import time
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
        self.level = logging.INFO
        self.print_gap: bool = True

        # DD Integration.
        self.datadog = None
        self.dd_stats = None
        self.dd_api_key: str = None
        self.dd_host: str = None
        self.dd_service: str = None
        self.dd_http_logs_active: bool = False
        self._dd_http_log_list: list = []
        self._dd_is_logging: bool = False

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
            "datadog": {
                "active": False,
                "api_key": None,
                "app_key": None,
                "http_log_active": False,
                "host": None,
                "service": None
            },
            "print_gap": 1
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

        print("Data Loaded", data)

        interval_unit = data["rotation"]["interval_unit"]
        interval_value = data["rotation"]["interval_value"]
        backup_count = data["rotation"]["backup_count"]
        self.print_gap = data["print_gap"]

        if data["file_logger"]["active"]:
            self._attach_file_logger(data["file_logger"]["path"], interval_unit, interval_value, backup_count)

        if data["json_logger"]["active"]:
            self._attach_json_logger(data["json_logger"]["path"], interval_unit, interval_value, backup_count)

        datadog_map = data["datadog"]
        if datadog_map["active"]:
            self._attach_datadog(
                datadog_map["api_key"],
                datadog_map["app_key"],
                datadog_map["http_log_active"],
                datadog_map["host"],
                datadog_map["service"])

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
        self.native_logger.setLevel(self.level)
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

    def _attach_datadog(
            self,
            api_key: str,
            app_key: str,
            http_logs_active: bool=False,
            host: Union[None, str]=None,
            service: Union[None, str]=None,
    ):
        import datadog
        self.datadog = datadog
        self.datadog.initialize(api_key=api_key, app_key=app_key, host=host)
        self.dd_stats = datadog.ThreadStats()
        self.dd_stats.start()

        self.dd_api_key = api_key
        self.dd_http_logs_active = http_logs_active
        self.dd_host = host
        self.dd_service = service

    def _queue_dd_log(self, data):

        data["service"] = self.dd_service
        data["hostname"] = self.dd_host
        data["date"] = time.time() * 1000
        self._dd_http_log_list.append(data)
        if not self._dd_is_logging:
            threading.Thread(target=self._async_log_loop).start()

    def _log_to_dd(self, data):

        if self.dd_http_logs_active:

            payload = json.dumps(data)
            command = f"curl " \
                      f"-X POST http://http-intake.logs.datadoghq.com/v1/input/{self.dd_api_key} " \
                      f"-H 'Content-Type: application/json' " \
                      f"-d '{payload}' &"
            os.system(
                command
            )

    def _async_log_loop(self):
        self._dd_is_logging = True

        try:
            while True:
                if len(self._dd_http_log_list) > 0:
                    next_item = self._dd_http_log_list.pop(0)
                    self._log_to_dd(next_item)
                else:
                    break

        except Exception as e:
            self.write("Logging Exception", {"exception": e}, level=logging.ERROR, is_internal=True)

        self._dd_is_logging = False

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
        if self.datadog is not None:
            # Transform data into tags.
            tags = [f"{k}:{v}" for k, v in data.items()]
            self.datadog.api.Event.create(title=title, text=text, tags=tags)

        message = f"{title}: {text}"
        self.write(message, data, logging.INFO)

    def increment(self, metric_name: str, value: Union[float, int]):
        self.write(f"Incrementing {metric_name}: {value}", None, logging.DEBUG)
        if self.dd_stats is not None:
            self.dd_stats.increment(metric_name, value)

    def gauge(self, metric_name: str, value: Union[float, int]):
        self.write(f"Gauging {metric_name}: {value}", None, logging.DEBUG)
        if self.dd_stats is not None:
            self.dd_stats.gauge(metric_name, value)
    
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

        if self.datadog is not None and self.dd_http_logs_active and not is_internal:
            data = {"message": message, "level": logging.getLevelName(level), "data": data}
            self._queue_dd_log(data)

        self.console_write(message, data, level, with_color=self.use_color)

    def console_write(self, message, data, level, with_color: bool = False):
        """ Custom function to write message to console. """

        if level < self.level:
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
