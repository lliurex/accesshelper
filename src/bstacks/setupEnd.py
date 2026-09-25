#!/usr/bin/python3
from llxaccessibility import llxaccessibility
from PySide2.QtWidgets import QWidget,QGridLayout,QScrollArea,QCheckBox,QLabel
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem,QHotkeyButton
from extras.i18n import *
from wdg.btnBar import btnBar

class setupEnd(QStackedWindowItem):
	def __init_stack__(self,*args):
		self.setProps(shortDesc="",
			description="",
			longDesc="",
			icon="preferences-desktop-accessibility",
			tooltip="",
			index=5)
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
		txt="<strong>{}</strong>".format(i18n["DOCK_MSG"])
		wbox.addWidget(QLabel(txt),0,0,1,2,Qt.AlignTop|Qt.AlignCenter)
		chkDefault=QCheckBox(i18n["DOCK_DEFAULT"])
		wbox.addWidget(chkDefault,1,0,1,2)
		chkStart=QCheckBox(i18n["DOCK_STARTUP"])
