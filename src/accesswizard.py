#!/usr/bin/env python3
import sys
import os
import subprocess
from PySide2.QtWidgets import QApplication,QLabel,QVBoxLayout
from QtExtraWidgets import QStackedWindow,QTableTouchWidget
from llxaccessibility import llxaccessibility

app=QApplication(["AccessWizard"])
config=QStackedWindow()
accClient=llxaccessibility.client()
if os.path.islink(__file__)==True:
	abspath=os.path.join(os.path.dirname(__file__),os.path.dirname(os.readlink(__file__)))
else:
	abspath=os.path.dirname(__file__)
config.addStacksFromFolder(os.path.join(abspath,"bstacks"))
config.setBanner(os.path.join(os.path.dirname(__file__),"rsrc","accesswizard_banner.png"))
config.setWiki("https://wiki.edu.gva.es/lliurex/tiki-index.php?page=accesswizard")
config.setIcon("accesswizard")
config.disableNavBar(True)
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
config.show()
config.toggleAutoNavigation()
app.exec_()
