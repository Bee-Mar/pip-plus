#!/usr/bin/env python3
from __future__ import annotations

from os import environ
from typing import List

COMPARISON_OPERATORS: List[str] = [
    "==",
    ">=",
    "<=",
    "~=",
    "!=",
    ">",
    "<",
]  # https://pip.pypa.io/en/stable/topics/dependency-resolution/

INSTALL: str = "install"
UNINSTALL: str = "uninstall"
REQUIREMENTS_TXT: str = "requirements.txt"
DEV_REQUIREMENTS_TXT: str = environ.get("PIP_PLUS_DEV_REQUIREMENTS_PATH", "requirements.dev.txt")
TEST_REQUIREMENTS_TXT: str = environ.get("PIP_PLUS_TEST_REQUIREMENTS_PATH", "test/requirements.txt")
DEV_ARG: str = "--dev"
TEST_ARG: str = "--test"
