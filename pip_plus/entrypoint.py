#!/usr/bin/env python3
from os import environ
from pathlib import Path, PosixPath
from sys import argv
from typing import List
import fileinput
from pip_plus.pinned_package import PinnedPackage
from pip_plus import utils
from pip_plus.constants import COMPARISON_OPERATORS, INSTALL, UNINSTALL, REQUIREMENTS_TXT


def main():
    if len(argv) < 3 or argv[1] != INSTALL and argv[1 ] != UNINSTALL:
        utils.run_user_pip_cmd(argv[1:])
        exit(0)

    pip_option: str = argv[1]
    virtual_env: str = environ.get("VIRTUAL_ENV")
    requirements_txt: PosixPath = Path(Path(virtual_env).parent / Path(REQUIREMENTS_TXT)) if virtual_env else Path(REQUIREMENTS_TXT)

    if not requirements_txt.exists():
        requirements_txt.touch()

    user_provided_packages: List[PinnedPackage] = utils.extract_user_provided_packages(argv[1:])

    utils.run_user_pip_cmd(argv[1:])

    packages_installed: List[PinnedPackage] = utils.get_installed_packages(user_provided_packages)
    current_requirements: List[PinnedPackage] = utils.get_current_requirements_txt(requirements_txt)

    for package in user_provided_packages:
        if pip_option == INSTALL:
            if package not in current_requirements:
                current_requirements.append(package)
        elif package in current_requirements:
            current_requirements.remove(package)

    with open(str(requirements_txt), "r+") as requirements_file:
        requirements_file.truncate(0)

        for requirement in current_requirements:
            requirements_file.write(f"{requirement}\n")


if __name__ == "__main__":
    main()
