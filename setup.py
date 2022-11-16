#!/usr/bin/env python3
from setuptools import setup, find_packages
from typing import List
from pip_plus.__version__ import semantic_version
from pathlib import Path

def load_requirements() -> List[str]:
    '''
    Parses requirements from requirements.txt to eliminate duplicate listing of packages

    Parameters:
        None

    Returns:
        requirements (List[str]): The package list the MMPM module requires
    '''

    if Path("requiements.txt").exists():
        requirements_file = open('./requirements.txt', 'r')
        requirements = requirements_file.read().splitlines()
        return requirements

    return []

setup(
    name="pip-plus",
    version=semantic_version,
    description="Pip-Plus",
    url="https://github.com/Bee-Mar/pip-plus",
    author="Brandon Marlowe",
    #download_url=f'https://github.com/Bee-Mar/mmpm/archive/{mmpm.mmpm.__version__}.tar.gz',
    author_email="bpmarlowe-software@protonmail.com",
    license="MIT",
    keywords="pip pip-plus pip_plus",
    packages=find_packages(),
    entry_points={"console_scripts": ["pip+=pip_plus.entrypoint:main"]},
    install_requires=load_requirements(),
    python_requires='>=3.7',
    include_package_data=True,
    zip_safe=True,
    setup_requires=['setuptools_scm'],
)
