#!/usr/bin/env python3
""" The main entrypoint for the PIP+ CLI application """
from __future__ import annotations

import sys
from os import environ
from pathlib import Path

from pip_plus import utils
from pip_plus.constants import DEV_ARG
from pip_plus.constants import INSTALL
from pip_plus.constants import TEST_ARG
from pip_plus.constants import UNINSTALL
from pip_plus.logger import PipPlusLogger


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

        if len(sys.argv) == 1 or (len(sys.argv) > 1 and sys.argv[1] == "help" or sys.argv[1] == "--help" or sys.argv[1] == "-h"):
            utils.run_user_pip_cmd(["help"])
            utils.usage()
            sys.exit(0)

        utils.run_user_pip_cmd(sys.argv[1:])
        sys.exit(0)

    pip_option = sys.argv[1]
    virtual_env = environ.get("VIRTUAL_ENV")

    updated_arguments, requirements_file = utils.determine_requirements_file(sys.argv)

    if requirements_file is None and updated_arguments is None:
        message = f"Invalid arguments, '{DEV_ARG}' and '{TEST_ARG}' options cannot be used simultaneously."
        print(f"ERROR: {message}")
        log.error(message)
        sys.exit(127)

    requirements_txt = Path(Path(virtual_env).parent / Path(requirements_file)) if virtual_env else Path(requirements_file)

    log.info(f"Targeting {str(requirements_txt)} following 'pip' execution.")

    requirements_txt.parent.mkdir(exist_ok=True)
    requirements_txt.touch(exist_ok=True)

    user_provided_packages = utils.extract_user_provided_packages(updated_arguments[1:])

    utils.run_user_pip_cmd(updated_arguments[1:])

    packages_installed = utils.get_installed_packages(user_provided_packages, venv=virtual_env)
    current_requirements = utils.extract_pinned_packages_from_requirements(requirements_txt)

    utils.update_requirements_file(
        requirements_txt,
        user_provided_packages,
        current_requirements,
        packages_installed,
        pip_option,
    )


if __name__ == "__main__":
    main()
