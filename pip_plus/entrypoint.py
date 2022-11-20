#!/usr/bin/env python3
""" The main entrypoint for the PIP+ CLI application """

from os import environ
from pathlib import Path, PosixPath
import sys
from typing import List
from pip_plus.pinned_package import PinnedPackage
from pip_plus import utils
from pip_plus.constants import (
    INSTALL,
    UNINSTALL,
    REQUIREMENTS_TXT,
)


def main():
    """
    Main entrypoint for the 'pip+' CLI. Extract user commands, run the user
    provided 'pip' command, and determine which packages should be
    appended/removed from the requirements.txt file.

    :param None:
    :returns None:
    """

    if len(sys.argv) < 3 or sys.argv[1] != INSTALL and sys.argv[1] != UNINSTALL:
        utils.run_user_pip_cmd(sys.argv[1:])
        sys.exit(0)

    pip_option: str = sys.argv[1]
    virtual_env: str = environ.get("VIRTUAL_ENV")
    requirements_txt: PosixPath = (
        Path(Path(virtual_env).parent / Path(REQUIREMENTS_TXT)) if virtual_env else Path(REQUIREMENTS_TXT)
    )

    if not requirements_txt.exists():
        requirements_txt.touch()

    user_provided_packages: List[PinnedPackage] = utils.extract_user_provided_packages(sys.argv[1:])

    utils.run_user_pip_cmd(sys.argv[1:])

    packages_installed: List[PinnedPackage] = utils.get_installed_packages(user_provided_packages)
    current_requirements: List[PinnedPackage] = utils.get_current_requirements_txt(requirements_txt)

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


if __name__ == "__main__":
    main()
