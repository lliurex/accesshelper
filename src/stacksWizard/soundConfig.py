#!/usr/bin/python3
from llxaccessibility import llxaccessibility
from PySide2.QtWidgets import QWidget,QGridLayout,QScrollArea,QCheckBox,QLabel
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem
from extras.i18n import *
from wdg.btnBar import btnBar

class soundConfig(QStackedWindowItem):
	def __init_stack__(self,*args):
		self.setProps(shortDesc="",
			description="",
			longDesc="",
			icon="preferences-desktop-accessibility",
			tooltip="",
			index=3)
		self.hideControlButtons()
	#def __init_stack__

	def _defScreenControlButtons(self):
		wdg=btnBar(self.parent)
		return(wdg)
	#def _defScreenControlButtons

	def __initScreen__(self):
		box=QGridLayout(self)
		scr=QScrollArea()
		scr.setWidgetResizable(True)
		wdg=QWidget()
		wbox=QGridLayout(wdg)
		lbl=QLabel()
		lbl.setText("<strong>{}</stong>".format(i18n["SND_LABEL"]))
		wbox.addWidget(lbl,0,0,1,1,Qt.AlignTop|Qt.AlignCenter)
		chkBootBeep=QCheckBox(i18n["SND_BOOT"])
		wbox.addWidget(chkBootBeep,1,0,1,1)
		chkSddmSound=QCheckBox(i18n["SND_START"])
		wbox.addWidget(chkSddmSound,2,0,1,1)
		chkSddmOrca=QCheckBox(i18n["SND_START_ORCA"])
		wbox.addWidget(chkSddmOrca,3,0,1,1)
		chkMonoSound=QCheckBox(i18n["SND_MONO"])
		wbox.addWidget(chkMonoSound,4,0,1,1)

		btns=self._defScreenControlButtons()
		wbox.addWidget(btns,5,0,1,1,Qt.AlignBottom)
		scr.setWidget(wdg)
		box.addWidget(scr)
	def updateScreen(self):
		pass

