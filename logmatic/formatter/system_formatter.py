# -*- coding: utf-8 -*-

"""
<Description>
"""
from logging import Formatter

__author__ = "Jakrin Juangbhanich"
__copyright__ = "Copyright 2019, GenVis Pty Ltd."
__email__ = "krinj@genvis.co"


class SystemFormatter(Formatter):

    def format(self, record):
        """ Override the default Formatter so we expand the data of the LogRecord. """
        record.message = record.getMessage()
        if self.usesTime():
            record.asctime = self.formatTime(record, self.datefmt)
        s = self.formatMessage(record)
        if record.exc_info:
            # Cache the traceback text to avoid converting it multiple times
            # (it's constant anyway)
            if not record.exc_text:
                record.exc_text = self.formatException(record.exc_info)
        if record.exc_text:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + record.exc_text
        if record.stack_info:
            if s[-1:] != "\n":
                s = s + "\n"
            s = s + self.formatStack(record.stack_info)
        return s
