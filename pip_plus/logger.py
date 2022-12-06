#!/usr/bin/env python3
import logging
from logging.handlers import RotatingFileHandler
from pathlib import PosixPath, Path
from os import environ
from json import dumps
from pip_plus.__version__ import semantic_version


class PipPlusLogger:
    """
    Wrapper class of the logging.Logger to initialize the logging object in
    a desired way.
    """

    _log: logging.Logger = None  # type: ignore

    @staticmethod
    def get_logger(module_name: str) -> logging.Logger:
        """
        A private method that interacts with the python logging module. The log
        level can be set by updating the environment variable named 'PIP_PLUS_LOG_LEVEL'
        to the desired log level.

        :param module_name: the name of the Python module calling the logger

        :returns logger: the logger object initialized with the provided module_name
        """

        home: str = str(Path.home())

        PipPlusLogger._log = logging.getLogger("pip_plus").getChild(module_name)

        pip_plus_log_dir: PosixPath = PosixPath(f"{home}/.local/share/pip-plus/log")
        pip_plus_log_dir.mkdir(exist_ok=True, parents=True)

        log_file_handler: RotatingFileHandler = RotatingFileHandler(
            f"{str(pip_plus_log_dir)}/pip-plus.log", maxBytes=2000, backupCount=5
        )

        PipPlusLogger._log.addHandler(log_file_handler)

        formatter: logging.Formatter = logging.Formatter(
            dumps(
                {
                    "date": "%(asctime)s",
                    "level": "%(levelname)s ",
                    "version": semantic_version,
                    "location": "%(name)s:%(funcName)s:%(lineno)d",
                    "message": "%(message)s",
                }
            ),
            datefmt="%Y-%m-%d %H:%M:%S",
        )

        log_file_handler.setFormatter(formatter)

        log_level = environ.get("PIP_PLUS_LOG_LEVEL", "INFO").upper()

        if log_level in ("INFO", "WARN", "DEBUG", "ERROR", "FATAL"):
            PipPlusLogger._log.setLevel(getattr(logging, log_level))
        else:
            # just in case the user didn't provide something that was usable
            PipPlusLogger._log.setLevel(logging.INFO)

        return PipPlusLogger._log
