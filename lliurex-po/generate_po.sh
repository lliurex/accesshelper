#!/bin/bash

PYTHON_FILES="../src/*.py ../src/stacks/*.py"

mkdir -p accesshelper

xgettext $UI_FILES $PYTHON_FILES -o accesshelper/accesshelper.pot


