# -*- coding: utf-8 -*-

"""
Extends JSON Formatter to include option things.
"""

from json_log_formatter import JSONFormatter

__author__ = "Jakrin Juangbhanich"
__email__ = "juangbhanich.k@gmail.com"


class ExtendedJSONFormatter(JSONFormatter):
    def json_record(self, message, extra, record):
        """Prepares a JSON payload which will be logged. """
        extra = super().json_record(message, extra, record)
        extra["levelname"] = record.levelname
        return extra
