#!/usr/bin/python3
import sys
import os,json
import shutil
from PySide6.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QComboBox,QHeaderView,QFileDialog,QScrollArea,QFrame
from PySide6 import QtGui
from PySide6 import QtMultimedia
from PySide6.QtCore import Qt,QSignalMapper,QSize,QThread,QObject,Signal,QUrl,QFile, QIODevice
from PySide6.QtUiTools import QUiLoader
from QtExtraWidgets import QTableTouchWidget,QKdeConfigWidget
import gettext
gettext.textdomain("accesswizard")
_ = gettext.gettext
import subprocess
from llxaccessibility import llxaccessibility
QString=type("")
