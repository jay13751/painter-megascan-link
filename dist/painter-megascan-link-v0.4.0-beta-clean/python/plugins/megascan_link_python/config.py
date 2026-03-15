"""Module containing classes for managing the config settings files or related."""

from __future__ import annotations

import configparser
from pathlib import Path
from typing import Dict, List

from . import utilities as util


DEFAULT_CONFIG: Dict[str, Dict[str, str]] = {
    "Meta": {"version": "2"},
    "Connection": {"port": "24981", "timeout": "5", "source": "fab"},
    "General": {
        "outputConsole": "false",
        "askcreateproject": "true",
        "selectafterimport": "true",
        "showDependencyError": "true",
        "debug_payload_logging": "false",
        "ignore_missing_optional_fields": "true",
    },
    "Bake": {
        "enabled": "false",
        "resolution": "[12,12]",
        "maxreardistance": "0.5",
        "maxfrontaldistance": "0.6",
        "average": "true",
        "relative": "true",
        "ignorebackface": "true",
        "antialiasing": "Subsampling 2x2",
    },
}


class ConfigSettings(object):
    path = None
    config = configparser.ConfigParser()
    opened = False

    @classmethod
    def setIniFilePath(cls, name: str):
        cls.path = Path(util.getAbsCurrentPath(name + ".ini"))

    @classmethod
    def getAsDict(cls) -> dict:
        cls.checkConfigState()
        return {s: dict(cls.config.items(s)) for s in cls.config.sections()}

    @classmethod
    def getConfigSettingAsList(cls, cat: str, prop: str, separator=",") -> List[str]:
        res = cls.getConfigSetting(cat, prop)
        if res == "":
            return []
        return res.split(separator)

    @classmethod
    def removeConfigSettings(cls, cat: str, prop: str, flush=True) -> bool:
        cls.checkConfigState()
        res = cls.config.remove_option(cat, prop)
        if flush:
            cls.flush()
        return res

    @classmethod
    def updateConfigSetting(cls, cat: str, prop: str, value: str, flush=True):
        cls.checkConfigState()
        if not cls.config.has_section(cat):
            cls.config.add_section(cat)
        cls.config[cat][prop] = str(value)
        if flush:
            cls.flush()

    @classmethod
    def getConfigSetting(cls, cat: str, prop: str, fallback="") -> str:
        cls.checkConfigState()
        return cls.config.get(cat, prop, fallback=fallback)

    @classmethod
    def getConfigCategory(cls, cat: str) -> dict:
        cls.checkConfigState()
        if cls.config.has_section(cat):
            return cls.config[cat]
        return {}

    @classmethod
    def checkConfigState(cls):
        if cls.path is None:
            raise RuntimeError("Config path has not been initialized")
        if not cls.opened:
            cls.config = configparser.ConfigParser()
            if cls.path.exists():
                cls.config.read(cls.path)
            cls._apply_defaults()
            cls.opened = True

    @classmethod
    def setUpInitialConfig(cls, defaults: configparser.ConfigParser | None = None):
        if cls.path is None:
            raise RuntimeError("Config path has not been initialized")
        cls.config = configparser.ConfigParser()
        if defaults is not None:
            cls.config.read_dict({section: dict(defaults[section]) for section in defaults.sections()})
        else:
            cls.config.read_dict(DEFAULT_CONFIG)
        if cls.path.exists():
            existing = configparser.ConfigParser()
            existing.read(cls.path)
            for section in existing.sections():
                if not cls.config.has_section(section):
                    cls.config.add_section(section)
                for key, value in existing.items(section):
                    cls.config[section][key] = value
        cls._apply_defaults()
        cls.flush()

    @classmethod
    def _apply_defaults(cls):
        changed = False
        for section, values in DEFAULT_CONFIG.items():
            if not cls.config.has_section(section):
                cls.config.add_section(section)
                changed = True
            for key, value in values.items():
                if not cls.config.has_option(section, key):
                    cls.config[section][key] = value
                    changed = True
        if cls.config.get("Meta", "version", fallback="0") != DEFAULT_CONFIG["Meta"]["version"]:
            cls.config["Meta"]["version"] = DEFAULT_CONFIG["Meta"]["version"]
            changed = True
        if changed and cls.path:
            with open(cls.path, "w", encoding="utf-8") as configFile:
                cls.config.write(configFile)

    @classmethod
    def checkIfOptionIsSet(cls, cat: str, prop: str, fallback="") -> bool:
        return cls.getConfigSetting(cat, prop, fallback).lower() in ["true", "yes", "y", "ok", "1"]

    @classmethod
    def flush(cls):
        with open(cls.path, "w", encoding="utf-8") as configFile:
            cls.config.write(configFile)
        cls.opened = False
        cls.checkConfigState()
