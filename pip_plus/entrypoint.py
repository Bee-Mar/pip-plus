#!/usr/bin/env python3
from os import environ
from pathlib import Path, PosixPath
from sys import argv
from typing import List, Dict, Set, Any
from subprocess import Popen, PIPE
import pkgutil
from importlib.metadata import version
import fileinput


class PinnedPackage:
    def __init__(self, name: str, version: str = "", comparison: str = "") -> None:
        self.name = name.strip()
        self.version = version.strip()
        self.comparison = comparison.strip()

    def __str__(self) -> str:
        return f"{self.name}{self.comparison}{self.version}"

    def __eq__(self, o) -> bool:
        if isinstance(o, PinnedPackage):
            return self.name == o.name

        return self.name == o


def __run_user_pip_cmd__(args: List[Any]) -> None:
    Popen(f"pip {' '.join(args)}", shell=True).wait()


def main():
    if len(argv) < 3 or argv[1] != "install" and argv[1] != "uninstall":
        __run_user_pip_cmd__(argv[1:])
        exit(0)

    pip_option: str = argv[1]
    virtual_env: str = environ.get("VIRTUAL_ENV")
    requirements_txt: PosixPath = Path(Path(virtual_env).parent / Path("requirements.txt")) if virtual_env else Path("requirements.txt")


    if not requirements_txt.exists():
        requirements_txt.touch()

    pinned_packages: List[PinnedPackage] = []

    for argument in argv[1:]:
        if argument.startswith("-") == False and argument != "install" and argument != "uninstall":
            argument = argument.replace(" ", "")

            found_comparison: bool = False

            for comparison in ["==", ">=", "<=", "~=", ">", "<"]:
                if argument.find(comparison) != -1:
                    found_comparison = True
                    split = argument.split(comparison)
                    pinned_packages.append(PinnedPackage(split[0], split[1], comparison))
                    break

            if not found_comparison:
                pinned_packages.append(PinnedPackage(argument))

    current_packages: List[str] = [package.name for package in pkgutil.iter_modules()]

    __run_user_pip_cmd__(argv[1:])

    packages_installed: List[PinnedPackage] = []

    for module in pkgutil.iter_modules():
        for package in pinned_packages:
            if module.name == package.name:
                try:
                    if not package.comparison and not package.version:
                        package.comparison = "~="
                        package.version = version(module.name)

                    packages_installed.append(package)
                except Exception as error:
                    pass

    updated_requirements: List[PinnedPackage] = []

    with open(str(requirements_txt)) as requirements:
        for line in requirements:
            found_comparison: bool = False

            for comparison in ["==", ">=", "<=", "~=", ">", "<"]:
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
        if pip_option == "install":
            if package not in updated_requirements:
                updated_requirements.append(package)
        elif package in updated_requirements:
            updated_requirements.remove(package)

    with open(str(requirements_txt), "r+") as requirements:
        requirements.truncate(0)

        for requirement in updated_requirements:
            requirements.write(f"{requirement}\n")


if __name__ == "__main__":
    main()
