#!/usr/bin/python3
from llxaccessibility import llxaccessibility
from PySide2.QtWidgets import QWidget,QGridLayout,QScrollArea,QCheckBox,QLabel
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem
from extras.i18n import *
from wdg.btnBar import btnBar

class helpersConfig(QStackedWindowItem):
	def __init_stack__(self,*args):
		self.setProps(shortDesc="",
			description="",
			longDesc="",
			icon="preferences-desktop-accessibility",
			tooltip="",
			index=4)
		self.hideControlButtons()
	#def __init_stack__

	def _defScreenControlButtons(self):
		wdg=btnBar(self.parent)
		return(wdg)
	#def _defScreenControlButtons

	def __initScreen__(self,*args):
		box=QGridLayout(self)
		scr=QScrollArea()
		scr.setWidgetResizable(True)
		wdg=QWidget()
		wbox=QGridLayout(wdg)
		txt="<strong>{}</strong>".format(i18n["HLP_MSG"])
		wbox.addWidget(QLabel(txt),0,0,1,1,Qt.AlignTop|Qt.AlignCenter)
		chkMouse=QCheckBox(i18n["HLP_MOUSE"])
		wbox.addWidget(chkMouse,1,0,1,1)
		chkStrip=QCheckBox(i18n["HLP_STRIP"])
		wbox.addWidget(chkStrip,2,0,1,1)
		chkBell=QCheckBox(i18n["HLP_BELL"])
		wbox.addWidget(chkBell,3,0,1,1)
		chkOsk=QCheckBox(i18n["HLP_OSK"])
		wbox.addWidget(chkOsk,4,0,1,1)
		btns=self._defScreenControlButtons()
		wbox.addWidget(btns,5,0,1,1,Qt.AlignBottom)
		scr.setWidget(wdg)
		box.addWidget(scr)
	#def __initScreen__

	def updateScreen(self,*args):
		pass
