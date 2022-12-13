<p align="center">
  <!-- badges start -->
  <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=L2ML7F8DTMAT2&currency_code=USD&source=ur" target="_blank">
    <img src="https://img.shields.io/badge/Donate-PayPal-green.svg" alt="PayPal">
  </a>
  <a href="http://choosealicense.com/licenses/mit" target="_blank">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License">
  </a>
  <a href="https://github.com/Bee-Mar/pip-plus-cli/actions" target="_blank">
    <img src="https://github.com/bee-mar/pip-plus-cli/actions/workflows/build.yml/badge.svg?master"
    alt="GitHub Actions">
  </a>
  <!-- wait to show once there are some decent download amounts
  <img src="https://static.pepy.tech/personalized-badge/pip-plus-cli?period=total&units=abbreviation&left_color=grey&right_color=blue&left_text=Downloads">
  <a href="https://pypi.org/project/pip-plus-cli" target="_blank">
    <img src="https://img.shields.io/pypi/v/pip-plus-cli.svg" alt="PyPI version">
  </a>
  -->
  <!-- badges end -->

  <!-- main title/logo -->
  <a href="https://www.paypal.com/cgi-bin/webscr?cmd=_donations&business=L2ML7F8DTMAT2&currency_code=USD&source=ur" target="_blank">
    <img src="assets/pip-plus-logo.png" alt="Pip-Plus-CLI">
  </a>
</p>

# Pip-Plus-CLI

| Author          | Contact                           |
| --------------- | --------------------------------- |
| Brandon Marlowe | bpmarlowe-software@protonmail.com |

The Pip-Plus-CLI is a wrapper around the `pip` command line application which automatically updates
the appropriate requirements.txt file with Python modules installed or removed from your
environment. This behavior already exists in other language specific package managers such as `NPM`.

## Examples

For example, if your current requirements.txt contained the following:

```sh
flask==2.2.2
```

and you ran `pip+ install requests==2.28.1`, your requirements.txt would be updated to contain

```sh
flask==2.2.2
requests==2.28.1
```

and if you ran `pip+ uninstall flask`, the requirements.txt would be again updated to contain:

```sh
requests==2.28.1
```

## Environment Variables and Options

The Pip-Plus-CLI accepts and executes all normal `pip` subcommands, but adds the options and envrionment variables:

| Environment Variable              | Usage                                                                                                                                       |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| `PIP_PLUS_DEV_REQUIREMENTS_PATH`  | Path to the dev requirements.txt. Default is set to 'requirements.dev.txt' in either your current directory, or relative to your virtualenv |
| `PIP_PLUS_TEST_REQUIREMENTS_PATH` | Path to test requirements.txt. Default is set to 'test/requirements.txt' in either your current directory, or relative to your virtualenv   |
| `PIP_PLUS_LOG_LEVEL`              | Set log level to one of (DEBUG, INFO, WARN, ERROR, FATAL) - Default log level is INFO. Logs are stored in '~/.local/share/pip-plus/log'     |

| Option   | Usage                                                        |
| -------- | ------------------------------------------------------------ |
| `--test` | Saves package information to PIP_PLUS_TEST_REQUIREMENTS_PATH |
| `--dev`  | Saves package information to PIP_PLUS_DEV_REQUIREMENTS_PATH  |

## Requirements File Paths

All file paths for the `requirements.txt`, `requirements.dev.txt` and `test/requirements.txt` are
either expected to be located in your current directory or relative to the active `VIRTUAL_ENV`. The
examples below detail which files are modified given situations with default values for the
Pip-Plus-CLI as well as with a virtual environment active.

### Examples with Default Environment Pip-Plus-CLI Environment Variables

| Environment Variable              | Value                |
| --------------------------------- | -------------------- |
| `PIP_PLUS_DEV_REQUIREMENTS_PATH`  | "" # (default value) |
| `PIP_PLUS_TEST_REQUIREMENTS_PATH` | "" # (default value) |

| Command                        | Current Directory | VIRTUAL_ENV | File Modified                    |
| ------------------------------ | ----------------- | ----------- | -------------------------------- |
| `pip+ install requests`        | `/tmp`            | ""          | `/tmp/requirements.txt`          |
| `pip+ install --dev requests`  | `/tmp`            | ""          | `/tmp/requirements.dev.txt`      |
| `pip+ install --test requests` | `/tmp`            | ""          | `/tmp/test/requirements.dev.txt` |

| Command                        | Current Directory | VIRTUAL_ENV       | File Modified                      |
| ------------------------------ | ----------------- | ----------------- | ---------------------------------- |
| `pip+ install requests`        | `/tmp`            | "/home/user/venv" | `/home/user/requirements.txt`      |
| `pip+ install --dev requests`  | `/tmp`            | "/home/user/venv" | `/home/user/requirements.dev.txt`  |
| `pip+ install --test requests` | `/tmp`            | "/home/user/venv" | `/home/user/test/requirements.txt` |

### Examples with Modified Environment Pip-Plus-CLI Environment Variables

| Environment Variable              | Value                   |
| --------------------------------- | ----------------------- |
| `PIP_PLUS_DEV_REQUIREMENTS_PATH`  | "dev-requirements.txt"  |
| `PIP_PLUS_TEST_REQUIREMENTS_PATH` | "test-requirements.txt" |

| Command                        | Current Directory | VIRTUAL_ENV | File Modified                |
| ------------------------------ | ----------------- | ----------- | ---------------------------- |
| `pip+ install requests`        | `/tmp`            | ""          | `/tmp/requirements.txt`      |
| `pip+ install --dev requests`  | `/tmp`            | ""          | `/tmp/dev-requirements.txt`  |
| `pip+ install --test requests` | `/tmp`            | ""          | `/tmp/test-requirements.txt` |

| Command                        | Current Directory | VIRTUAL_ENV       | File Modified                      |
| ------------------------------ | ----------------- | ----------------- | ---------------------------------- |
| `pip+ install requests`        | `/tmp`            | "/home/user/venv" | `/home/user/requirements.txt`      |
| `pip+ install --dev requests`  | `/tmp`            | "/home/user/venv" | `/home/user/dev-requirements.txt`  |
| `pip+ install --test requests` | `/tmp`            | "/home/user/venv" | `/home/user/test-requirements.txt` |
