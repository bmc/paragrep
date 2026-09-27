#!/usr/bin/env bash
#
# Run Python checkers and formatters.

echo "Checking types ..."
pyright paragrep || exit 1

echo "Linting ..."
ruff check paragrep

echo "Sorting imports in $i"
isort paragrep/*.py

echo "Formatting $i with black"
black paragrep/*.py
