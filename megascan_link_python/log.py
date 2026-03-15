"""Logging helpers for the plugin."""

from __future__ import annotations

import logging

from . import config
from . import utilities as util


class LoggerLink(object):
    _name = ""
    _logger = None
    _isSetup = False

    @classmethod
    def setLoggerName(cls, name: str):
        if cls._name == "" and cls._isSetup is False:
            cls._name = name
            cls._logger = logging.getLogger(name)

    @classmethod
    def setUpLogger(cls):
        if cls._name == "":
            cls.setLoggerName("megascanlink")
        cls._isSetup = True
        logFormatter = logging.Formatter("%(asctime)s [%(name)s] [%(levelname)s] %(message)s")
        for handler in list(cls._logger.handlers):
            cls._logger.removeHandler(handler)
        filehandler = logging.FileHandler(util.getAbsCurrentPath("{}.log".format(cls._name)), mode="a", encoding="utf-8")
        filehandler.setFormatter(logFormatter)
        cls._logger.addHandler(filehandler)
        cls._logger.setLevel(logging.DEBUG)

    @classmethod
    def Log(cls, msg: str, logLevel=logging.INFO):
        conf = config.ConfigSettings()
        if not cls._isSetup:
            cls.setUpLogger()
        if logLevel == logging.INFO:
            lvl = "INFO"
            cls._logger.info(msg)
        elif logLevel == logging.WARNING:
            lvl = "WARNING"
            cls._logger.warning(msg)
        elif logLevel == logging.ERROR:
            lvl = "ERROR"
            cls._logger.error(msg)
        else:
            lvl = "DEBUG"
            cls._logger.debug(msg)
        if conf.checkIfOptionIsSet("General", "outputConsole") or logLevel >= logging.INFO:
            print("[{}][{}] {}".format(cls._name, lvl, msg))
