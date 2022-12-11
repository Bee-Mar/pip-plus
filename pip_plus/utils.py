#!/usr/bin/env python3
from __future__ import annotations

import importlib.metadata
import os
import site
import sys
from pathlib import PosixPath
from subprocess import CalledProcessError
from subprocess import Popen
from typing import Any
from typing import List
from typing import Set
from typing import Tuple

import pkg_resources

from pip_plus.constants import COMPARISON_OPERATORS
from pip_plus.constants import DEV_REQUIREMENTS_TXT
from pip_plus.constants import INSTALL
from pip_plus.constants import REQUIREMENTS_TXT
from pip_plus.constants import TEST_REQUIREMENTS_TXT
from pip_plus.constants import UNINSTALL
from pip_plus.logger import PipPlusLogger
from pip_plus.pinned_package import PinnedPackage

log = PipPlusLogger.get_logger(__name__)


def usage() -> None:  # pragma: no cover
    print(
        "\nPip-Plus Options:\n",
        " --test\t\t\t\tSaves package information to PIP_PLUS_TEST_REQUIREMENTS_PATH\n",
        " --dev\t\t\t\t\tSaves package information to PIP_PLUS_DEV_REQUIREMENTS_PATH",
    )

    print(
        "\nPip-Plus Environment Variables:\n",
        " PIP_PLUS_DEV_REQUIREMENTS_PATH\tPath to the dev requirements.txt. Default is set to requirements.dev.txt\n",
        " PIP_PLUS_TEST_REQUIREMENTS_PATH\tPath to test requirements.txt. Default is set to 'test/requirements.txt'\n",
        " PIP_PLUS_LOG_LEVEL\t\t\tSet log level to one of (DEBUG, INFO, WARN, ERROR, FATAL) - Default is INFO\n",
        "\t\t\t\t\tLogs are stored in ~/.local/share/pip-plus/log",
    )

    print(
        "\nPip-Plus Usage:\n ",
        "pip+ --test <command> [options]\n",
        " pip+ --dev <command> [options]\n",
        " pip+ <command> [options]",
    )

    log.debug(
        "User did not provide 'install', 'uninstall', '-r', or '--requirement' arguments. Running 'pip' normally.",
    )


def determine_requirements_file(arguments: List[Any]) -> Tuple[List[Any], str]:
    """
    Determines the correct requirements file name to use based on user arguments.

    :param arguments:
        user provided arguments passed to 'pip+'

    :returns updated_arguments, requirements_file:
        the modified list of arguments and corresponding
    """

    requirements_file: str = REQUIREMENTS_TXT

    if "--test" in arguments and "--dev" in arguments:
        log.debug("Invalid arguments. User provided both --dev and --test flags.")
        return None, None  # type: ignore

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

    :param arguments:
        arguments passed to 'pip'

    :returns none:
        None
    """

    pip_command_string: str = f"pip {' '.join(arguments)}"
    log.debug(f"Executing '{pip_command_string}'")

    try:
        with Popen(pip_command_string, shell=True) as pip_command:
            pip_command.wait()
    except CalledProcessError as error:
        log.error(f"Encountered error when running '{pip_command_string}': {str(error)}")


def extract_user_provided_packages(arguments: List[str]) -> List[PinnedPackage]:
    """
    Given the user arguments provided to pip+, the package names, versions and
    comparison_operator operators are extracted.

    :param arguments:
        the user provided arguments which are eventually passed to 'pip'

    :returns user_provided_packages:
        the list of extracted packages, which may or may not include version numbers
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

    log.debug(f"Extracted packages {[str(pkg) for pkg in user_provided_packages]} from user arguments")
    return user_provided_packages


def get_installed_packages(user_provided_packages: List[PinnedPackage], venv: str = "") -> List[PinnedPackage]:
    """
    This is intended to be executed after a 'pip' command to capture the
    packages that were successfully installed. If a version number and
    comparison_operator operator was provided by the user prior to installation, those
    are captured. If not, the '~=' operator is stored.

    :param user_provided_packages:
        the list of packages the user wanted installed

    :param venv:
        the VIRTUAL_ENV, if it is active

    :returns pinned_packages:
        the list of packages which were successfully installed
    """

    if venv:
        # the user may have pyenv installed and are using multiple versions of python
        # this is a more reliable way of getting the python version's directory name vs sys.version_info
        site.addsitedir(f"{venv}/{os.listdir(os.path.join(venv, 'lib'))[0]}/site-packages")

    # the working_set needs to get refreshed because it is created at import
    # time and becomes stale after the 'pip' command executes
    importlib.reload(pkg_resources)

    existing_packages: Set[str] = {pkg.key for directory in sys.path for pkg in pkg_resources.find_distributions(directory)}

    packages_installed: List[PinnedPackage] = []

    for package in user_provided_packages:
        if package.name in existing_packages:
            try:
                if not package.comparison_operator and not package.version:
                    package.comparison_operator = "~="
                    package.version = importlib.metadata.version(package.name)
            except importlib.metadata.PackageNotFoundError as error:
                log.error(str(error))
            finally:
                packages_installed.append(package)

    log.debug(f"Found matching packages installed {packages_installed}")
    return packages_installed


def extract_pinned_packages_from_requirements(
    requirements_txt: PosixPath,
) -> List[PinnedPackage]:
    """
    Parses the current requirements.txt as a List[PinnedPackage].

    :param requirements_txt:
        a PosixPath to the requirements.txt

    :returns current_requirements:
        the List[PinnedPackage] matching those in the requirements.txt
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

    log.debug(f"Found current requirements of {current_requirements}")
    return current_requirements


def update_requirements_file(
    requirements_txt: PosixPath,
    user_provided_packages: List[str],
    current_requirements: List[str],
    packages_installed: List[PinnedPackage],
    pip_option: str,
) -> None:
    """
    Updates the appropriate requirements file with all of the packages
    installed along with the matching version number. If user chose to remove
    packages, those are removed from the requirements file.

    :param requirements_txt:
        the file to update

    :param user_provided_packages:
        the list of packages the user passed in as arguments

    :param current_requirements:
        the list of packages found in the requirements file prior to executing this function

    :param packages_installed:
        the list of packages installed after executing the pip command desired by the user

    :param pip_option:
        either the 'install' or 'uninstall' option

    :returns none:
        None
    """

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

    message: str = f"Updated requirements: {str(requirements_txt)}"
    log.info(message)
    print(message)
