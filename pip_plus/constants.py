#!/usr/bin/env python3
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
DEV_REQUIREMENTS_TXT: str = "requirements.dev.txt"
TEST_REQUIREMENTS_TXT: str = "test/requirements.txt"
