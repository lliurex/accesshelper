#!/usr/bin/python3
from PySide2.QtWidgets import QGridLayout
from PySide2 import QtGui
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem
from wdg.configPane import QConfigPane
from extras.i18n import *

class theme(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.setProps(shortDesc=i18n.get("THEME_MENU"),
		    description=i18n.get('THEME_DESCRIPTION'),
		    longDesc=i18n.get('THEME_DESCRIPTION'),
			icon="preferences-desktop-theme",
			tooltip=i18n.get("THEME_TOOLTIP"),
			index=3,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.hideControlButtons()
	#def __init__

	def __initScreen__(self):
		lay=QGridLayout(self)
		apps=[{"THEME_LOOK":["kcm_desktoptheme","THEME_LOOKDSC","preferences-desktop-theme"]},
			{"THEME_COLO":["kcm_colors","THEME_COLODSC","preferences-desktop-color"]},
			{"THEME_FONT":["kcm_fonts","THEME_FONTDSC","preferences-desktop-font"]},
			{"THEME_MICE":["kcm_cursortheme","THEME_MICEDSC","preferences-desktop-mouse"]}
			]
		wdg=QConfigPane(apps)
		lay.addWidget(wdg,0,0,1,1)
	#def __initScreen__

	def fakeKey(self,*args):
		ev=args[0]
		if ev.key()==Qt.Key_Left:
			self.parent.lstNav.setFocus()
		else:
			self.lstApps.keyPressEvent2(*args)
			ev.ignore()
		return True
	#def fakeKey

	def focusInEvent(self,*args):
		self.lstApps.setFocus()
	#def focusInEvent

	def updateScreen(self):
		pass
	#def updateScreen

