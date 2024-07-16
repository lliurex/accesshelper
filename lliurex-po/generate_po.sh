#!/bin/bash

PYTHON_FILES="../src/*.py ../src/stacks/*.py ../src/tools/*.py ../src/dock/*.py ../src/dock/extras/*.py ../kwin/scripts/kwin-ocrwindow/contents/ui/tts.py"
mkdir -p accesswizard
xgettext $UI_FILES $PYTHON_FILES -o accesswizard/accesswizard.pot

QML_FILES="../kwin/plasmoids/net.lliurex.accesswizard/contents/ui/main.qml"
mkdir -p plasma-accesswizard
xgettext --from-code=UTF-8 -C --kde -ci18n $QML_FILES -o plasma-accesswizard/plasma_applet_net.lliurex.accesswizard.pot
