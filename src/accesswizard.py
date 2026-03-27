#!/usr/bin/env python3
import sys
import os
import subprocess
from PySide6.QtWidgets import QApplication,QLabel,QVBoxLayout
from PySide6.QtCore import Qt
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
#accClient.say(MSG_DISCLAIMER)
#accClient.say(MSG_DISCLAIMER_TEXT)
#accClient.say(MSG_OPTIONS)
if os.path.islink(__file__)==True:
	abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
else:
	abspath=os.path.dirname(__file__)
config.addStacksFromFolder(os.path.join(abspath,"stacks"))
config.setBanner(os.path.join(os.path.dirname(__file__),"rsrc","accesswizard_banner.png"))
config.setWiki("https://wiki.edu.gva.es/lliurex/tiki-index.php?page=accesswizard")
config.setIcon("accesswizard")
fakePortrait=QLabel()
lay=QVBoxLayout(fakePortrait)
text="<strong>{}</strong><br>".format(MSG_DISCLAIMER)
text+="<p>{}</p>".format(MSG_DISCLAIMER_TEXT)
text+="<p>{}</p>".format(MSG_OPTIONS)
lbl=QLabel(text)
lay.addWidget(lbl)
wdg=config.lstPortrait
config.stkPan.removeWidget(config.lstPortrait)
lay.addWidget(wdg)
config.layout().addWidget(fakePortrait,1,1)
config.lstPortrait=fakePortrait
config.show()
(w,h) = app.primaryScreen().size().toTuple()
config.setMinimumWidth(int(w*0.9))
config.setMinimumHeight(int(h*0.8))
font=config.font()
size=font.pointSize()
#minimum font size
if size<16:
	font.setPointSize(font.pointSize()+4)
	config.setFont(font)
config.toggleAutoNavigation()
app.exec()
