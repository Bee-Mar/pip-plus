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
    if len(argv) < 3 or argv[1] != INSTALL and argv[1] != UNINSTALL:
        utils.run_user_pip_cmd(argv[1:])
        exit(0)

    pip_option: str = argv[1]
    virtual_env: str = environ.get("VIRTUAL_ENV")
    requirements_txt: PosixPath = Path(Path(virtual_env).parent / Path(REQUIREMENTS_TXT)) if virtual_env else Path(REQUIREMENTS_TXT)

    if not requirements_txt.exists():
        requirements_txt.touch()

    pinned_packages: List[PinnedPackage] = utils.extract_pinned_packages(argv[1:])

    utils.run_user_pip_cmd(argv[1:])

    packages_installed: List[PinnedPackage] = utils.get_installed_packages(pinned_packages)

    updated_requirements: List[PinnedPackage] = []

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

                    updated_requirements.append(pinned_package)
                    break

            if not found_comparison:
                updated_requirements.append(PinnedPackage(line))

    for package in pinned_packages:
        if pip_option == INSTALL:
            if package not in updated_requirements:
                updated_requirements.append(package)
        elif package in updated_requirements:
            updated_requirements.remove(package)

    with open(str(requirements_txt), "r+") as requirements_file:
        requirements_file.truncate(0)

        for requirement in updated_requirements:
            requirements_file.write(f"{requirement}\n")


if __name__ == "__main__":
    main()
