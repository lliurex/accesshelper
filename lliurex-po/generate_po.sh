#!/bin/bash

PYTHON_FILES="../src/*.py ../src/stacks/*.py"

mkdir -p accesshelper
mkdir -p access_helper

xgettext $UI_FILES $PYTHON_FILES -o access_helper/access_helper.pot


