#!/usr/bin/env python3
from typing import List
from faker import Faker
from pip_plus import utils


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
