#! /usr/bin/env bash
black --exclude venv/ .
isort *.py --virtual-env venv
