#!/bin/bash

PYTHON_FILES="../src/*.py ../src/stacks/*.py ../src/tools/*.py ../src/dock/*.py ../src/dock/extras/*.py"

mkdir -p accesswizard

xgettext $UI_FILES $PYTHON_FILES -o accesswizard/accesswizard.pot


