#!/usr/bin/env python3
from typing import List, Any
from pip_plus.pinned_package import PinnedPackage
from pip_plus.constants import COMPARISON_OPERATORS, INSTALL, UNINSTALL
from subprocess import Popen
from importlib.metadata import version
from pathlib import PosixPath
import pkgutil

def run_user_pip_cmd(arguments: List[Any]) -> None:
    """
    Executes a 'pip' command in a subprocess.

    :param arguments: arguments passed to 'pip'
    :returns: None

    """

    try:
        Popen(f"pip {' '.join(arguments)}", shell=True).wait()
    except Exception:
        pass


def extract_user_provided_packages(arguments: List[str]) -> List[PinnedPackage]:
    """
    Given the user arguments provided to pip+, the package names, versions and
    comparison operators are extracted.

    :param arguments: the user provided arguments which are eventually passed to 'pip'
    :returns: the list of extracted packages, which may or may not include version numbers
    """

    user_provided_packages: List[PinnedPackage] = []

    for argument in arguments:
        if argument.startswith("-") == False and argument != INSTALL and argument != UNINSTALL:
            argument = argument.replace(" ", "")

            found_comparison: bool = False

            for comparison in COMPARISON_OPERATORS:
                if argument.find(comparison) != -1:
                    found_comparison = True
                    split = argument.split(comparison)
                    user_provided_packages.append(PinnedPackage(split[0], split[1], comparison))
                    break

            if not found_comparison:
                user_provided_packages.append(PinnedPackage(argument))

    return user_provided_packages


def get_installed_packages(user_provided_packages: List[PinnedPackage]) -> List[str]:
    """
    This is intended to be executed after a 'pip' command to capture the
    packages that were successfully installed. If a version number and
    comparison operator was provided by the user prior to installation, those
    are captured. If not, the '~=' operator is stored.

    :param user_provided_packages: the list of packages the user wanted installed
    :returns pinned_packages: the list of packages which were successfully installed
    """

    packages_installed: List[PinnedPackage] = []

    for module in pkgutil.iter_modules():
        for package in user_provided_packages:
            if module.name == package.name:
                if not package.comparison and not package.version:
                    package.comparison = "~="
                    package.version = version(module.name)

                packages_installed.append(package)

    return packages_installed


def get_current_requirements_txt(requirements_txt: PosixPath) -> List[PinnedPackage]:
    """
    Parses the current requirements.txt as a List[PinnedPackage].

    :param requirements_txt: a PosixPath to the requirements.txt
    :returns current_requirements: the List[PinnedPackage] matching those in the requirements.txt
    """

    current_requirements: List[PinnedPackage] = []

    with open(str(requirements_txt)) as requirements_file:
        for line in requirements_file:
            found_comparison: bool = False

            for comparison in COMPARISON_OPERATORS:
                if line.find(comparison) != -1:
                    found_comparison = True
                    split: List[str] = line.split(comparison)
                    pinned_package: PinnedPackage = PinnedPackage(split[0])

                    try:
                        pinned_package.comparison = comparison
                        pinned_package.version = split[1].strip()
                    except Exception as error:
                        pass

                    current_requirements.append(pinned_package)
                    break

            if not found_comparison:
                current_requirements.append(PinnedPackage(line))

    return current_requirements
