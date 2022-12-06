#!/usr/bin/env python3
from setuptools import setup, find_packages
from typing import List
from pip_plus.__version__ import semantic_version
from pathlib import Path


def load_requirements() -> List[str]:
    """
    Parses requirements from requirements.txt to eliminate duplicate listing of packages

    :param none: None

    :returns requiements: List[str]
        The list of packages required by the module
    """

    requirements: List[str] = []

    if Path("requirements.txt").exists():
        with open("requirements.txt") as requirements_file:
            requirements = requirements_file.read().splitlines()

    return requirements


setup(
    name="pip-plus-cli",
    version=semantic_version,
    description="Pip-Plus",
    long_description="The Pip-Plus CLI automatically updates requirements.txt following install/removal of packages",
    url="https://github.com/Bee-Mar/pip-plus",
    author="Brandon Marlowe",
    download_url=f"https://github.com/Bee-Mar/pip-plus/archive/refs/tags/v{semantic_version}.tar.gz",
    author_email="bpmarlowe-software@protonmail.com",
    license="MIT",
    keywords="pip pip-plus pip_plus",
    packages=find_packages(),
    entry_points={"console_scripts": ["pip+=pip_plus.entrypoint:main"]},
    install_requires=load_requirements(),
    python_requires=">=3.7",
    include_package_data=True,
    zip_safe=True,
    setup_requires=["setuptools_scm"],
)
