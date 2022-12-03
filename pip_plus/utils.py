#!/usr/bin/env python3
import pkgutil
import importlib.metadata
from typing import List, Any, Tuple
from subprocess import Popen, CalledProcessError
from pathlib import PosixPath
from pip_plus.pinned_package import PinnedPackage
from pip_plus.constants import COMPARISON_OPERATORS, INSTALL, UNINSTALL
from pip_plus.logger import PipPlusLogger
from pip_plus.constants import REQUIREMENTS_TXT, DEV_REQUIREMENTS_TXT, TEST_REQUIREMENTS_TXT

log = PipPlusLogger.get_logger(__name__)


def determine_requirements_file(arguments: List[Any]) -> Tuple[List[Any], str]:
    """
    Determines the correct requirements file name to use based on user arguments.

    :param arguments: user provided arguments passed to 'pip+'

    :returns: Tuple[List[Any], str]
    """

    requirements_file: str = REQUIREMENTS_TXT

    if "--test" in arguments and "--dev" in arguments:
        return None, None

    if "--test" in arguments:
        requirements_file = TEST_REQUIREMENTS_TXT
        arguments.remove("--test")
        log.debug("'--test' argument provided by user.")
    elif "--dev" in arguments:
        requirements_file = DEV_REQUIREMENTS_TXT
        arguments.remove("--dev")
        log.debug("'--dev' argument provided by user.")

    return arguments, requirements_file


# there really isn't a point in testing this
def run_user_pip_cmd(arguments: List[Any]) -> None:  # pragma: no cover
    """
    Executes a 'pip' command in a subprocess.

    :param arguments: arguments passed to 'pip'

    :returns none: None
    """

    try:
        with Popen(f"pip {' '.join(arguments)}", shell=True) as pip_command:
            pip_command.wait()
    except CalledProcessError:
        pass


def extract_user_provided_packages(arguments: List[str]) -> List[PinnedPackage]:
    """
    Given the user arguments provided to pip+, the package names, versions and
    comparison_operator operators are extracted.

    :param arguments: the user provided arguments which are eventually passed to 'pip'
    :returns: the list of extracted packages, which may or may not include version numbers
    """

    user_provided_packages: List[PinnedPackage] = []

    for argument in arguments:
        if argument.startswith("-") is False and argument != INSTALL and argument != UNINSTALL:
            argument = argument.replace(" ", "")

            found_comparison_operator: bool = False

            for comparison_operator in COMPARISON_OPERATORS:
                if argument.find(comparison_operator) != -1:
                    found_comparison_operator = True
                    split = argument.split(comparison_operator)
                    user_provided_packages.append(PinnedPackage(split[0], split[1], comparison_operator))
                    break

            if not found_comparison_operator:
                user_provided_packages.append(PinnedPackage(argument))

    return user_provided_packages


def get_installed_packages(user_provided_packages: List[PinnedPackage]) -> List[str]:
    """
    This is intended to be executed after a 'pip' command to capture the
    packages that were successfully installed. If a version number and
    comparison_operator operator was provided by the user prior to installation, those
    are captured. If not, the '~=' operator is stored.

    :param user_provided_packages: the list of packages the user wanted installed
    :returns pinned_packages: the list of packages which were successfully installed
    """

    packages_installed: List[PinnedPackage] = []

    for module in pkgutil.iter_modules():
        for package in user_provided_packages:
            if module.name == package.name:
                if not package.comparison_operator and not package.version:
                    package.comparison_operator = "~="
                    package.version = importlib.metadata.version(module.name)

                packages_installed.append(package)

    return packages_installed


def extract_pinned_packages_from_requirements(requirements_txt: PosixPath) -> List[PinnedPackage]:
    """
    Parses the current requirements.txt as a List[PinnedPackage].

    :param requirements_txt: a PosixPath to the requirements.txt
    :returns current_requirements: the List[PinnedPackage] matching those in the requirements.txt
    """

    current_requirements: List[PinnedPackage] = []

    with open(str(requirements_txt), "r", encoding="utf-8") as requirements_file:
        for line in requirements_file:
            found_comparison_operator: bool = False

            for comparison_operator in COMPARISON_OPERATORS:
                if line.find(comparison_operator) != -1:
                    found_comparison_operator = True
                    split: List[str] = line.split(comparison_operator)
                    pinned_package: PinnedPackage = PinnedPackage(split[0])

                    if len(split) > 1:
                        pinned_package.comparison_operator = comparison_operator
                        pinned_package.version = split[1].strip()

                    current_requirements.append(pinned_package)
                    break

            if not found_comparison_operator:
                current_requirements.append(PinnedPackage(line))

    return current_requirements


def update_requirements_file(
    requirements_txt: PosixPath,
    user_provided_packages: List[str],
    current_requirements: List[str],
    packages_installed: List[PinnedPackage],
    pip_option: str,
) -> None:
    for package in user_provided_packages:
        if pip_option == INSTALL:
            if package not in current_requirements and package in packages_installed:
                current_requirements.append(package)
        elif package in current_requirements:
            current_requirements.remove(package)

    with open(str(requirements_txt), "r+", encoding="utf-8") as requirements_file:
        requirements_file.truncate(0)

        for requirement in current_requirements:
            requirements_file.write(f"{requirement}\n")
