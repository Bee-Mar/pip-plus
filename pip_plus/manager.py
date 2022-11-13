#!/usr/bin/env python3
from os import environ
from pathlib import Path, PosixPath
from sys import argv
from typing import List, Dict, Set, Any
from subprocess import Popen, PIPE
import pkgutil
from importlib.metadata import version
import fileinput


def __run_user_pip_cmd__(args: List[Any]) -> None:
    Popen(f"pip {' '.join(args)}", shell=True).wait()


def __get_module_name__(pkg_name: str) -> str:
    return pkg_name.split("==")[0].lower()

if __name__ == "__main__":

    if len(argv) < 3 or argv[1] != "install" and argv[1] != "uninstall":
        __run_user_pip_cmd__(argv[1:])
        exit(0)

    pip_option: str = argv[1]
    virtual_env: str = environ.get("VIRTUAL_ENV")
    requirements_txt: PosixPath = Path(Path(virtual_env).parent / Path("requirements.txt")) if virtual_env else Path("requirements.txt")

    if not requirements_txt.exists():
        requirements_txt.touch()

    provided_package_names: List[str] = []

    for argument in argv[1:]:
        if argument.startswith("-") == False and argument != "install" and argument != "uninstall":
            provided_package_names.append(__get_module_name__(argument))

    current_packages: List[str] = [package.name for package in pkgutil.iter_modules()]

    __run_user_pip_cmd__(argv[1:])

    packages_installed: Dict[str, str] = {}

    for module in pkgutil.iter_modules():
        if module.name in provided_package_names:
            try:
                packages_installed[module.name.lower()] = version(module.name)
            except Exception as error:
                pass

    updated_requirements: List[str] = []

    with open(str(requirements_txt)) as requirements:
        for line in requirements:
            updated_requirements.append(__get_module_name__(line))

    for package in provided_package_names:
        if pip_option == "install" and package not in updated_requirements:
            updated_requirements.append(package)
        elif package in updated_requirements:
            updated_requirements.remove(package)

    with open(str(requirements_txt), "r+") as requirements:
        requirements.truncate(0)

        for requirement in updated_requirements:
            if requirement in packages_installed:
                requirements.write(f"{requirement.lower()}=={packages_installed[requirement]}\n")
            else:
                try:
                    requirements.write(f"{requirement.lower()}=={version(requirement)}\n")
                except Exception as error:
                    pass
