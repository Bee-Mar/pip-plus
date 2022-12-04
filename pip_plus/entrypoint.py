#!/usr/bin/env python3
""" The main entrypoint for the PIP+ CLI application """
import sys
from os import environ
from pathlib import Path, PosixPath
from typing import List
from pip_plus.pinned_package import PinnedPackage
from pip_plus import utils
from pip_plus.logger import PipPlusLogger
from pip_plus.constants import INSTALL, UNINSTALL, DEV_ARG, TEST_ARG


def main():
    """
    Main entrypoint for the 'pip+' CLI. Extract user commands, run the user
    provided 'pip' command, and determine which packages should be
    appended/removed from the requirements.txt file.

    :param None:
    :returns None:
    """

    log = PipPlusLogger.get_logger(__name__)
    log_level = environ.get("PIP_PLUS_LOG_LEVEL", "INFO").upper()

    log.info(f"User set PIP_PLUS_LOG_LEVEL to '{log_level}")

    if (
        len(sys.argv) < 3
        or (sys.argv[1] != INSTALL and sys.argv[1] != UNINSTALL)
        or "-r" in sys.argv
        or "--requirement" in sys.argv
    ):
        if sys.argv[1] == "help" or sys.argv[1] == "--help" or sys.argv[1] == "-h":
            utils.help()
        utils.run_user_pip_cmd(sys.argv[1:])
        sys.exit(0)

    pip_option: str = sys.argv[1]
    virtual_env: str = environ.get("VIRTUAL_ENV")

    updated_arguments, requirements_file = utils.determine_requirements_file(sys.argv)

    if requirements_file is None and updated_arguments is None:
        message = f"Invalid arguments, '{DEV_ARG}' and '{TEST_ARG}' options cannot be used simultaneously."
        print(f"ERROR: {message}")
        log.error(message)
        exit(127)

    requirements_txt: PosixPath = (
        Path(Path(virtual_env).parent / Path(requirements_file)) if virtual_env else Path(requirements_file)
    )

    log.info(f"Targeting {str(requirements_txt)} following 'pip' execution.")

    requirements_txt.parent.mkdir(exist_ok=True)
    requirements_txt.touch(exist_ok=True)

    user_provided_packages: List[PinnedPackage] = utils.extract_user_provided_packages(updated_arguments[1:])

    utils.run_user_pip_cmd(updated_arguments[1:])

    packages_installed: List[PinnedPackage] = utils.get_installed_packages(user_provided_packages)
    current_requirements: List[PinnedPackage] = utils.extract_pinned_packages_from_requirements(requirements_txt)

    utils.update_requirements_file(
        requirements_txt,
        user_provided_packages,
        current_requirements,
        packages_installed,
        pip_option,
    )


if __name__ == "__main__":
    main()
