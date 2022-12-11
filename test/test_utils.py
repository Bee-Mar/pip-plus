#!/usr/bin/env python3
from __future__ import annotations

import random
import tempfile
from os import chdir
from os import mkdir
from pathlib import Path
from pathlib import PosixPath
from shutil import rmtree
from typing import List
from unittest.mock import patch

from faker import Faker

from pip_plus import utils
from pip_plus.constants import COMPARISON_OPERATORS
from pip_plus.constants import DEV_ARG
from pip_plus.constants import DEV_REQUIREMENTS_TXT
from pip_plus.constants import REQUIREMENTS_TXT
from pip_plus.constants import TEST_ARG
from pip_plus.constants import TEST_REQUIREMENTS_TXT
from pip_plus.pinned_package import PinnedPackage


def random_int(min_value=1, max_value=10):
    fake: Faker = Faker()
    return fake.pyint(min_value=min_value, max_value=max_value)


def create_random_pinned_packages(with_version: bool = False) -> List[PinnedPackage]:
    fake: Faker = Faker()

    if with_version:
        return [
            PinnedPackage(
                fake.word(),
                version=f"{random_int()}.{random_int()}.{random_int()}",
                comparison_operator=random.choice(COMPARISON_OPERATORS),
            )
            for _ in range(random_int())
        ]

    return [PinnedPackage(fake.word()) for _ in range(random_int())]


def test_pinned_package_setters():
    fake: Faker = Faker()
    random_name: str = fake.word()
    random_version: str = f"{random_int()}.{random_int()}.{random_int()}"
    random_comparison_operator: str = random.choice(COMPARISON_OPERATORS)
    fixture: PinnedPackage = PinnedPackage(random_name, version=random_version, comparison_operator=random_comparison_operator)

    assert fixture.name == random_name
    assert fixture.version == random_version
    assert fixture.comparison_operator == random_comparison_operator


def test_pinned_package_equals_succeeeds_with_string():
    fake: Faker = Faker()
    random_package_name: str = fake.word()
    fixture: PinnedPackage = PinnedPackage(random_package_name)
    assert fixture == random_package_name


def test_pinned_package_equals_succeeeds_with_pinned_package():
    fake: Faker = Faker()
    random_package_name: str = fake.word()
    fixture: PinnedPackage = PinnedPackage(random_package_name)
    random_package: PinnedPackage = PinnedPackage(random_package_name)
    assert fixture == random_package


def test_pinned_package_equals_fails_with_string():
    fake: Faker = Faker()
    fixture: PinnedPackage = PinnedPackage(fake.word())
    assert fixture != fake.word()


def test_pinned_package_equals_fails_with_pinned_package():
    fake: Faker = Faker()
    fixture: PinnedPackage = PinnedPackage(fake.word())
    random_package: PinnedPackage = PinnedPackage(fake.word())
    assert fixture != random_package


def test_pinned_package_to_string_with_name_only():
    fake: Faker = Faker()
    random_name: str = fake.word()
    fixture: PinnedPackage = PinnedPackage(random_name)
    assert str(fixture) == random_name


def test_pinned_package_to_string_with_version_and_name():
    fake: Faker = Faker()
    random_name: str = fake.word()
    random_version: str = (
        f"{fake.pyint(min_value=0, max_value=10)}.{fake.pyint(min_value=0, max_value=10)}.{fake.pyint(min_value=0, max_value=10)}"
    )
    random_comparison_operator: str = random.choice(COMPARISON_OPERATORS)

    fixture: PinnedPackage = PinnedPackage(random_name, version=random_version, comparison_operator=random_comparison_operator)
    assert str(fixture) == f"{random_name}{random_comparison_operator}{random_version}"


def test_extract_user_provided_packages_for_installation():
    fake: Faker = Faker()

    fake_install_arguments: List[str] = [fake.word() for index in range(10)]

    extracted_packages = utils.extract_user_provided_packages(["install"] + fake_install_arguments)

    assert len(fake_install_arguments) == len(extracted_packages)

    assert "install" not in extracted_packages
    assert "uninstall" not in extracted_packages

    for package in extracted_packages:
        assert package in fake_install_arguments


def test_extract_user_provided_packages_for_removal():
    fake: Faker = Faker()

    fake_uninstall_arguments: List[str] = [fake.word() for index in range(10)]

    extracted_packages = utils.extract_user_provided_packages(["uninstall"] + fake_uninstall_arguments)

    assert len(fake_uninstall_arguments) == len(extracted_packages)

    assert "install" not in extracted_packages
    assert "uninstall" not in extracted_packages

    for package in extracted_packages:
        assert package in fake_uninstall_arguments


def test_extract_user_provided_packages_for_installation_with_additional_args():
    fake: Faker = Faker()

    fake_install_arguments: List[str] = [fake.word() for index in range(10)]
    random_extra_args: List[str] = [f"--{fake.word()}-{fake.word()}"]

    extracted_packages = utils.extract_user_provided_packages(
        ["install", "--upgrade", f"--{fake.word()}" f"--{fake.word()}-{fake.word()}"] + fake_install_arguments,
    )

    assert len(fake_install_arguments) == len(extracted_packages)

    assert "install" not in extracted_packages
    assert "uninstall" not in extracted_packages

    for extra_arg in random_extra_args:
        assert extra_arg not in extracted_packages

    for package in extracted_packages:
        assert package in fake_install_arguments


def test_extract_user_provided_packages_for_removal_with_additional_args():
    fake: Faker = Faker()

    fake_uninstall_arguments: List[str] = [fake.word() for index in range(10)]
    random_extra_args: List[str] = [f"--{fake.word()}-{fake.word()}"]

    extracted_packages = utils.extract_user_provided_packages(["uninstall"] + random_extra_args + fake_uninstall_arguments)

    assert len(fake_uninstall_arguments) == len(extracted_packages)

    assert "install" not in extracted_packages
    assert "uninstall" not in extracted_packages

    for extra_arg in random_extra_args:
        assert extra_arg not in extracted_packages

    for package in extracted_packages:
        assert package in fake_uninstall_arguments


def test_get_installed_packages_with_version_provided():
    fake: Faker = Faker()

    random_provided_packages: List[PinnedPackage] = create_random_pinned_packages(True)

    with patch("pkgutil.iter_modules") as patched_iter_modules:
        patched_iter_modules.return_value = random_provided_packages

        result = utils.get_installed_packages(random_provided_packages)

        for pkg in result:
            assert pkg in random_provided_packages


def test_get_installed_packages_without_version_provided():
    fake: Faker = Faker()

    length: int = random_int()
    semantic_version: str = f"{random_int()}.{random_int()}.{random_int()}"

    random_provided_packages: List[PinnedPackage] = [PinnedPackage(fake.word()) for _ in range(length)]

    with patch("pkgutil.iter_modules") as patched_iter_modules, patch("importlib.metadata.version") as patched_version:
        patched_iter_modules.return_value = random_provided_packages
        patched_version.return_value = semantic_version

        result = utils.get_installed_packages(random_provided_packages)

        for pkg in result:
            assert pkg in random_provided_packages
            assert pkg.version == semantic_version
            assert pkg.comparison_operator == "~="


def test_determine_requirements_file_returns_test_requirements():
    fake: Faker = Faker()
    arguments, requirements = utils.determine_requirements_file([TEST_ARG] + [fake.word() for _ in range(random_int())])

    assert TEST_ARG not in arguments
    assert requirements == TEST_REQUIREMENTS_TXT


def test_determine_requirements_file_returns_dev_requirements():
    fake: Faker = Faker()
    arguments, requirements = utils.determine_requirements_file([DEV_ARG] + [fake.word() for _ in range(random_int())])

    assert DEV_ARG not in arguments
    assert requirements == DEV_REQUIREMENTS_TXT


def test_determine_requirements_file_returns_none():
    fake: Faker = Faker()
    arguments, requirements = utils.determine_requirements_file([DEV_ARG, TEST_ARG] + [fake.word() for _ in range(random_int())])
    assert arguments is None and requirements is None


def test_determine_requirements_file_returns_regular_requirements():
    fake: Faker = Faker()
    arguments, requirements = utils.determine_requirements_file([fake.word() for _ in range(random_int())])

    assert requirements == REQUIREMENTS_TXT


def test_extract_pinned_packages_from_requirements_is_empty():
    tempdir: str = tempfile.mkdtemp()
    mkdir(f"{tempdir}/test")  # just in case the test requirement is selected
    chdir(tempdir)

    random_requirements_file: str = random.choice([TEST_REQUIREMENTS_TXT, DEV_REQUIREMENTS_TXT, REQUIREMENTS_TXT])

    requirements_txt: PosixPath = Path(Path(tempdir) / Path(random_requirements_file))
    requirements_txt.touch(exist_ok=True)
    requirements: List[PinnedPackage] = utils.extract_pinned_packages_from_requirements(requirements_txt)
    assert len(requirements) == 0


def test_extract_pinned_packages_from_requirements_matches_with_version():
    fake: Faker = Faker()
    tempdir: str = tempfile.mkdtemp()
    mkdir(f"{tempdir}/test")  # just in case the test requirement is selected

    random_requirements_file: str = random.choice([TEST_REQUIREMENTS_TXT, DEV_REQUIREMENTS_TXT, REQUIREMENTS_TXT])

    requirements_txt: PosixPath = Path(Path(tempdir) / Path(random_requirements_file))
    requirements_txt.touch(exist_ok=True)

    expected_requirements: List[PinnedPackage] = create_random_pinned_packages(True)

    with open(str(requirements_txt), "r+", encoding="utf-8") as requirements_file:
        for requirement in expected_requirements:
            requirements_file.write(f"{str(requirement)}\n")

    requirements: List[PinnedPackage] = utils.extract_pinned_packages_from_requirements(requirements_txt)

    for index, requirement in enumerate(requirements):
        assert requirement.comparison_operator == expected_requirements[index].comparison_operator
        assert requirement.name == expected_requirements[index].name
        assert requirement.version == expected_requirements[index].version

    rmtree(tempdir)


def test_extract_pinned_packages_from_requirements_matches_without_version():
    fake: Faker = Faker()
    tempdir: str = tempfile.mkdtemp()
    mkdir(f"{tempdir}/test")  # just in case the test requirement is selected

    random_requirements_file: str = random.choice([TEST_REQUIREMENTS_TXT, DEV_REQUIREMENTS_TXT, REQUIREMENTS_TXT])

    requirements_txt: PosixPath = Path(Path(tempdir) / Path(random_requirements_file))
    requirements_txt.touch(exist_ok=True)

    expected_requirements: List[PinnedPackage] = create_random_pinned_packages()

    with open(str(requirements_txt), "r+", encoding="utf-8") as requirements_file:
        for requirement in expected_requirements:
            requirements_file.write(f"{str(requirement)}\n")

    requirements: List[PinnedPackage] = utils.extract_pinned_packages_from_requirements(requirements_txt)

    for index, requirement in enumerate(requirements):
        assert requirement.comparison_operator == ""
        assert requirement.name == expected_requirements[index].name
        assert requirement.version == ""

    rmtree(tempdir)


def test_update_requirements_file_install_option():
    fake: Faker = Faker()
    tempdir: str = tempfile.mkdtemp()
    mkdir(f"{tempdir}/test")  # just in case the test requirement is selected

    random_requirements_file: str = random.choice([TEST_REQUIREMENTS_TXT, DEV_REQUIREMENTS_TXT, REQUIREMENTS_TXT])

    requirements_txt: PosixPath = Path(Path(tempdir) / Path(random_requirements_file))
    requirements_txt.touch(exist_ok=True)

    user_provided_packages: List[PinnedPackage] = create_random_pinned_packages(True)
    current_requirements: List[PinnedPackage] = create_random_pinned_packages(True)
    packages_installed: List[PinnedPackage] = user_provided_packages

    utils.update_requirements_file(
        requirements_txt,
        user_provided_packages,
        current_requirements,
        packages_installed,
        "install",
    )

    updated_requirements = utils.extract_pinned_packages_from_requirements(requirements_txt)

    for package in packages_installed:
        assert package in updated_requirements

    rmtree(tempdir)


def test_update_requirements_file_uninstall_option():
    fake: Faker = Faker()
    tempdir: str = tempfile.mkdtemp()
    mkdir(f"{tempdir}/test")  # just in case the test requirement is selected

    random_requirements_file: str = random.choice([TEST_REQUIREMENTS_TXT, DEV_REQUIREMENTS_TXT, REQUIREMENTS_TXT])

    requirements_txt: PosixPath = Path(Path(tempdir) / Path(random_requirements_file))
    requirements_txt.touch(exist_ok=True)

    user_provided_packages: List[PinnedPackage] = create_random_pinned_packages(True)
    current_requirements: List[PinnedPackage] = create_random_pinned_packages(True)
    packages_installed: List[PinnedPackage] = user_provided_packages

    utils.update_requirements_file(
        requirements_txt,
        user_provided_packages,
        current_requirements,
        packages_installed,
        "uninst all",
    )

    updated_requirements = utils.extract_pinned_packages_from_requirements(requirements_txt)

    for package in packages_installed:
        assert package not in updated_requirements

    rmtree(tempdir)
