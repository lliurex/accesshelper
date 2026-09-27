#!/usr/bin/python3
from llxaccessibility import llxaccessibility
from PySide2.QtWidgets import QWidget,QGridLayout,QScrollArea,QCheckBox,QLabel,QPushButton
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem,QHotkeyButton
from extras.i18n import *
from lib.threadLib import thProcess
from wdg.btnBar import btnBar

class dockConfig(QStackedWindowItem):
	def __init_stack__(self,*args):
		self.setProps(shortDesc="",
			description="",
			longDesc="",
			icon="preferences-desktop-accessibility",
			tooltip="",
			index=4)
		self.hideControlButtons()
		self.exe=thProcess()
	#def __init_stack__

	def _defDockHotkey(self):
		wdg=QWidget()
		lay=QGridLayout(wdg)
		lblHotkey=QLabel(i18n["DOCK_HOTKEY"])
		lay.addWidget(lblHotkey,0,0,1,1)
		btnHotkey=QHotkeyButton(i18n["DOCK_HOTKEY"])
		lay.addWidget(btnHotkey,0,1,1,1,Qt.AlignLeft)
		return(wdg)
	#def _defDockHotkey

	def _defScreenControlButtons(self):
		wdg=btnBar(self.parent)
		return(wdg)
	#def _defScreenControlButtons

	def _launchConfig(self):
		self.exe.setCmd("/home/lliurex/git/accesshelper/src/dock/accessdock-config.py")
		self.exe.start()

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
		wbox.addWidget(chkStart,2,0,1,2)
	#	dockHotKey=self._defDockHotkey()
	#	wbox.addWidget(dockHotKey,3,0,1,1)
		btnDockConfig=QPushButton(i18n["DOCK_CONFIG_DOCK"])
		btnDockConfig.clicked.connect(self._launchConfig)
		wbox.addWidget(btnDockConfig,3,0,1,2)
		btns=self._defScreenControlButtons()
		wbox.addWidget(btns,4,0,1,2,Qt.AlignBottom)
		scr.setWidget(wdg)
		box.addWidget(scr)
	#def __initScreen__

	def updateScreen(self,*args):
		pass

