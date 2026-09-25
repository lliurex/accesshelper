#!/usr/bin/python3
from llxaccessibility import llxaccessibility
from PySide2.QtWidgets import QWidget,QGridLayout,QScrollArea,QCheckBox,QPushButton
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem,QScrollLabel
from wdg.btnBar import btnBar
from lib.threadLib import thProcess
from extras.i18n import *

class setupWizard(QStackedWindowItem):
	def __init_stack__(self,*args):
		self.setProps(shortDesc="",
			description="",
			longDesc="",
			icon="preferences-desktop-accessibility",
			tooltip="",
			index=0)
		self.hideControlButtons()
		self.accessibility=llxaccessibility.client()
		self.exe=thProcess()
	#def __init__

	def _defDisclaimer(self):
		lbl=QScrollLabel(styled=False)
		lbl.setWordWrap(True)
		txt="<p align=\"center\"><strong>{}</strong></p>".format(i18n["MSG_DISCLAIMER"])
		txt+="<p>{}</p>".format(i18n["MSG_DISCLAIMER_TEXT_1"])
		txt+="<p>{}</p>".format(i18n["MSG_DISCLAIMER_TEXT_2"])
		lbl.setText(txt)
		return(lbl)
	#def _defDisclaimer

	def _launchOrcaConfig(self):
		self.exe.setCmd("orca","-s")
		self.exe.start()
	#def _launchOrcaConfig

	def _defOrcaButtons(self):
		wdg=QWidget()
		lay=QGridLayout(wdg)
		self.chkEnable=QCheckBox(i18n["SETUP_CHK_ORCA"])
		self.chkEnable.setChecked(True)
		lay.addWidget(self.chkEnable)
		btnConfigOrca=QPushButton(i18n["SETUP_CONFIG_ORCA"])
		btnConfigOrca.clicked.connect(self._launchOrcaConfig)
		self.chkEnable.stateChanged.connect(btnConfigOrca.setEnabled)
		lay.addWidget(btnConfigOrca)
		return(wdg)
	#def _orcaControlButtons

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
		self.lblDisclaimer=self._defDisclaimer()
		wbox.addWidget(self.lblDisclaimer,0,0,1,1,Qt.AlignTop)
		orcaBtns=self._defOrcaButtons()
		wbox.addWidget(orcaBtns,1,0,1,1,Qt.AlignTop)
		btns=self._defScreenControlButtons()
		wbox.addWidget(btns)
		scr.setWidget(wdg)
		box.addWidget(scr)
	#def __initScreen__

	def updateScreen(self,*args):
		self.accessibility.a11Manager.disableOrca()
		if self.chkEnable.isChecked()==True:
			self.accessibility.say(self.lblDisclaimer.accessibleDescription())
			self.chkEnable.setFocus()
			#self.accessibility.a11Manager.enableOrca()
		else:
			self.accessibility.a11Manager.disableOrca()
		self.setCursor(Qt.ArrowCursor)
	#def updateScreen
#class
