#! /usr/bin/env bash
black --exclude venv/ .
isort . --virtual-env venv
