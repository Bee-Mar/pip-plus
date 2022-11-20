#!/usr/bin/env python3
from typing import List, Any
from pip_plus.pinned_package import PinnedPackage
from pip_plus.constants import COMPARISON_OPERATORS, INSTALL, UNINSTALL
from subprocess import Popen
from importlib.metadata import version
import pkgutil

def run_user_pip_cmd(args: List[Any]) -> None:
    Popen(f"pip {' '.join(args)}", shell=True).wait()

def extract_pinned_packages(arguments: List[str]) -> List[PinnedPackage]:
    pinned_packages: List[PinnedPackage] = []

    for argument in arguments:
        if argument.startswith("-") == False and argument != INSTALL and argument != UNINSTALL:
            argument = argument.replace(" ", "")

            found_comparison: bool = False

            for comparison in COMPARISON_OPERATORS:
                if argument.find(comparison) != -1:
                    found_comparison = True
                    split = argument.split(comparison)
                    pinned_packages.append(PinnedPackage(split[0], split[1], comparison))
                    break

            if not found_comparison:
                pinned_packages.append(PinnedPackage(argument))

    return pinned_packages


def get_installed_packages(pinned_packages: List[PinnedPackage]) -> List[str]:
    packages_installed: List[PinnedPackage] = []

    for module in pkgutil.iter_modules():
        for package in pinned_packages:
            if module.name == package.name:
                if not package.comparison and not package.version:
                    package.comparison = "~="
                    package.version = version(module.name)

                packages_installed.append(package)

    return packages_installed

