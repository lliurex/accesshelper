#!/usr/bin/env python3
import sys
import os
import subprocess
from PySide2.QtWidgets import QApplication,QLabel,QVBoxLayout
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindow,QTableTouchWidget
from llxaccessibility import llxaccessibility
import gettext
gettext.textdomain('accesswizard')
_ = gettext.gettext

MSG_DISCLAIMER=_("Wizard of LliureX for configuring accessibility tools")
MSG_DISCLAIMER_TEXT=_("Press \"Escape\" to stop reading. \"F5\" for read it from beginning")
MSG_OPTIONS=_("Navigate through options with \"Tab\" or arrows.")
app=QApplication(["Access Wizard"])
config=QStackedWindow()
accClient=llxaccessibility.client()
if os.path.islink(__file__)==True:
	abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
else:
	abspath=os.path.dirname(__file__)
config.addStacksFromFolder(os.path.join(abspath,"stacks"))
config.setBanner(os.path.join(os.path.dirname(__file__),"rsrc","accesswizard_banner.png"))
config.setWiki("https://wiki.edu.gva.es/lliurex/tiki-index.php?page=accesswizard")
config.setIcon("accesswizard")
config.show()
(w,h) = app.primaryScreen().size().toTuple()
config.setMinimumHeight(int(h*0.6))
config.setMinimumWidth(int(w*0.7))
font=config.font()
size=font.pointSize()
#minimum font size
if size<16:
	font.setPointSize(font.pointSize()+4)
	config.setFont(font)
app.exec_()
