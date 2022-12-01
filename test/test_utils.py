#!/usr/bin/env python3
from typing import List
from faker import Faker
from pip_plus import utils
from pip_plus.pinned_package import PinnedPackage
from pip_plus.constants import COMPARISON_OPERATORS
from unittest.mock import MagicMock, patch
import random


def test_pinned_package_setters():
    fake: Faker = Faker()
    random_name: str = fake.word()
    random_version: str = f"{fake.pyint(min_value=0, max_value=10)}.{fake.pyint(min_value=0, max_value=10)}.{fake.pyint(min_value=0, max_value=10)}"
    random_comparison_operator: str = random.choice(COMPARISON_OPERATORS)
    fixture: PinnedPackage = PinnedPackage(
        random_name, version=random_version, comparison_operator=random_comparison_operator
    )

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


def test_pinned_package_to_string_with_name_only():
    fake: Faker = Faker()
    random_name: str = fake.word()
    random_version: str = f"{fake.pyint(min_value=0, max_value=10)}.{fake.pyint(min_value=0, max_value=10)}.{fake.pyint(min_value=0, max_value=10)}"
    random_comparison_operator: str = random.choice(COMPARISON_OPERATORS)

    fixture: PinnedPackage = PinnedPackage(
        random_name, version=random_version, comparison_operator=random_comparison_operator
    )
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
        ["install", "--upgrade", f"--{fake.word()}" f"--{fake.word()}-{fake.word()}"] + fake_install_arguments
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

    extracted_packages = utils.extract_user_provided_packages(
        ["uninstall"] + random_extra_args + fake_uninstall_arguments
    )

    assert len(fake_uninstall_arguments) == len(extracted_packages)

    assert "install" not in extracted_packages
    assert "uninstall" not in extracted_packages

    for extra_arg in random_extra_args:
        assert extra_arg not in extracted_packages

    for package in extracted_packages:
        assert package in fake_uninstall_arguments


def test_get_installed_packages():
    fake: Faker = Faker()

    random_provided_packages: List[PinnedPackage] = [
        PinnedPackage(fake.word(), version="1.0.0", comparison_operator="!=")
        for _ in range(fake.pyint(min_value=1, max_value=10))
    ]

    with patch("pkgutil.iter_modules") as patched_iter_modules:
        patched_iter_modules.return_value = random_provided_packages

        result = utils.get_installed_packages(random_provided_packages)

        for pkg in result:
            assert pkg in random_provided_packages
