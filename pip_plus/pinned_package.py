#!/usr/bin/env python3
from typing import Any

class PinnedPackage:
    def __init__(self, name: str, version: str = "", comparison: str = "") -> None:
        self.name = name.strip()
        self.version = version.strip()
        self.comparison = comparison.strip()

    def __str__(self) -> str:
        return f"{self.name}{self.comparison}{self.version}"

    def __eq__(self, other: str) -> bool:
        if isinstance(other, PinnedPackage):
            return self.name == other.name

        return self.name == other

