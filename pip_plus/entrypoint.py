#!/usr/bin/env python3
""" The main entrypoint for the PIP+ CLI application """

from os import environ
from pathlib import Path, PosixPath
import sys
from typing import List
from pip_plus.pinned_package import PinnedPackage
from pip_plus import utils
from pip_plus.logger import PipPlusLogger
from pip_plus.constants import (
    INSTALL,
    UNINSTALL,
    REQUIREMENTS_TXT,
    DEV_REQUIREMENTS_TXT,
    TEST_REQUIREMENTS_TXT,
)


def main():
    """
    Main entrypoint for the 'pip+' CLI. Extract user commands, run the user
    provided 'pip' command, and determine which packages should be
    appended/removed from the requirements.txt file.

    :param None:
    :returns None:
    """

    log = PipPlusLogger.get_logger(__name__)

    if (
        len(sys.argv) < 3
        or (sys.argv[1] != INSTALL and sys.argv[1] != UNINSTALL)
        or "-r" in sys.argv
        or "--requirement" in sys.argv
    ):

        # if sys.argv[1] == "help" or sys.argv[1] == "--help" or sys.argv[1] == "-h":
        #     print("\nPip-Plus Options:\n ",
        #           "--test\t\tSaves package information to './test/requirements.txt'\n",
        #           " --dev\t\tSaves package information to ./requirements.dev.txt")

        #     print("\nPip-Plus Usage:\n ",
        #           "pip+ --test <command> [options]\n",
        #           " pip+ --dev <command> [options]\n",
        #           " pip+ <command> [options]")

        log.info(
            "User did not provide 'install', 'uninstall', '-r', or '--requirement' arguments. Running 'pip' normally."
        )
        utils.run_user_pip_cmd(sys.argv[1:])
        sys.exit(0)

    pip_option: str = sys.argv[1]
    virtual_env: str = environ.get("VIRTUAL_ENV")

    requirements_file: str = REQUIREMENTS_TXT

    if "--test" in sys.argv:
        requirements_file = TEST_REQUIREMENTS_TXT
        sys.argv.remove("--test")
        log.debug("'--test' argument provided by user.")
    elif "--dev" in sys.argv:
        requirements_file = DEV_REQUIREMENTS_TXT
        sys.argv.remove("--dev")
        log.debug("'--dev' argument provided by user.")

    requirements_txt: PosixPath = (
        Path(Path(virtual_env).parent / Path(requirements_file)) if virtual_env else Path(requirements_file)
    )

    log.info(f"Targeting {str(requirements_txt)} following 'pip' execution.")

    requirements_txt.parent.mkdir(exist_ok=True)
    requirements_txt.touch(exist_ok=True)

    user_provided_packages: List[PinnedPackage] = utils.extract_user_provided_packages(sys.argv[1:])

    log.debug(
        f"Extracted packages {[str(pkg) for pkg in user_provided_packages]} from user arguments. Running 'pip' command."
    )

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
