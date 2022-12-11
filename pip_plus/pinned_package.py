#!/usr/bin/env python3
""" Contains class definition of PinnedPackage """
from __future__ import annotations


class PinnedPackage:
    """
    The PinnedPackage class represents the basic Python package version
    information. The 'name', 'version' and 'comparison_operator' are
    extracted from a pinned package such as 'some_package>=1.0.0'.

    In the example above:
    'name' = 'some_package'
    'version' = '1.0.0'
    'comparison_operator' = '>='
    """

    def __init__(self, name: str, version: str = "", comparison_operator: str = "") -> None:
        self.name = name.strip()
        self.version = version.strip()
        self.comparison_operator = comparison_operator.strip()

    def __str__(self) -> str:
        return f"{self.name}{self.comparison_operator}{self.version}"

    def __eq__(self, other: object) -> bool:
        if isinstance(other, PinnedPackage):
            return self.name == other.name
        if isinstance(other, str):
            return self.name == other

        return self.name == other
