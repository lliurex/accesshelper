#!/usr/bin/python3
import os
from PySide2.QtWidgets import QGridLayout
from PySide2 import QtGui
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem, QPushInfoButton,QTableTouchWidget
from wdg.configPane import QConfigPane
from extras.i18n import *

class accessibility(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.setProps(shortDesc=i18n.get("ACCESS_MENU"),
			description=i18n.get('ACCESS_DESCRIPTION'),
			longDesc=i18n.get('ACCESS_DESCRIPTION'),
			icon="preferences-desktop-accessibility",
			tooltip=i18n.get("ACCESS_TOOLTIP"),
			index=1,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.hideControlButtons()
	#def __init__

	def __initScreen__(self):
		lay=QGridLayout(self)
		rsrcDir=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","rsrc")
		apps=[{"ACCE":["ACCEDSC","preferences-desktop-accessibility"]},
			{"ORCA":["ORCADSC",""]},
			{"LTTS":["LTTSDSC",os.path.join(rsrcDir,"ttsmanager.png")]},
			{"DOCK": ["DOCKDSC",os.path.join(rsrcDir,"accessdock.png")]},
			{"ANTI": ["ANTIDSC",""]},
			{"EVIA": ["EVIADSC",""]}
			]
		wdg=QConfigPane(apps)
		lay.addWidget(wdg,0,0,1,1)
	#def __initScreen__

	def updateScreen(self):
		pass
	#def updateScreen

