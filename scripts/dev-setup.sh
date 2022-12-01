#!/usr/bin/env bash

if [[ ! -d venv ]]; then
    python3 -m venv venv
fi

if [[ "$VIRTUAL_ENV" != "" ]]; then
    pip install -r ./requirements.dev.txt -r test/requirements.txt
fi
