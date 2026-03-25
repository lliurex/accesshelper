#!/usr/bin/python3
import sys
import os,json
import shutil
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QComboBox,QHeaderView,QFileDialog,QScrollArea,QFrame
from PySide2 import QtGui
from PySide2 import QtMultimedia
from PySide2.QtCore import Qt,QSignalMapper,QSize,QThread,QObject,Signal,QUrl,QFile, QIODevice
from PySide2.QtUiTools import QUiLoader
from QtExtraWidgets import QTableTouchWidget,QKdeConfigWidget
import gettext
gettext.textdomain("accesswizard")
_ = gettext.gettext
import subprocess
from llxaccessibility import llxaccessibility
QString=type("")
