#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication,QLineEdit, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QListWidget
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
from . import functionHelper
_ = gettext.gettext
QString=type("")

i18n={
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Manage profiles"),
	"MENUDESCRIPTION":_("Load and save custom profiles"),
	"TOOLTIP":_("Use profile templates for quick configuration"),
	"SAVE":_("Save profile"),
	"LOAD":_("Load profile")
	}

class profiles(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("access Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('application-vnd.iccprofile')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=11
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.config={}
		self.optionChanged=[]
		self.wrkDir="/usr/share/accesshelper/profiles"
		self.lst_profiles=QListWidget()
		self.hideControlButtons()
	#def __init__

	def _load_screen(self):
		self.box=QVBoxLayout()
		self.setLayout(self.box)
		self.widgets={}
		self.level='user'
		self.refresh=True
		self.box.addWidget(self.lst_profiles)
		btn_load=QPushButton(i18n.get("LOAD"))
		self.box.addWidget(btn_load)
		btn_save=QPushButton(i18n.get("SAVE"))
		self.inp_name=QLineEdit()
		wdg_save=QWidget()
		hbox=QHBoxLayout()
		wdg_save.setLayout(hbox)
		hbox.addWidget(self.inp_name)
		hbox.addWidget(btn_save)
		self.box.addWidget(wdg_save)

		self.lst_profiles.currentRowChanged.connect(self._updateText)
		btn_load.clicked.connect(self.loadProfile)
		btn_save.clicked.connect(self.writeConfig)
		self.updateScreen()
	#def _load_screen

	def _updateText(self,*args):
		widget=self.lst_profiles.currentItem()
		if widget:
			fProfile=widget.text()
			self.inp_name.setText(fProfile)
	#def _updateText

	def updateScreen(self):
		self.lst_profiles.clear()
		if os.path.isdir(self.wrkDir):
			for f in os.listdir(self.wrkDir):
				if len(f)>20:
					f=f[0:19]
				self.lst_profiles.addItem(f)
		self.lst_profiles.sortItems()
	#def _udpate_screen

	def loadProfile(self,*args):
		self._debug("Restoring snapshot")
		name=self.inp_name.text()
		name=os.path.basename(name)
		if len(name)>20:
			name=name[0:19]
		functionHelper.restore_snapshot(self.wrkDir,name)
		self.optionChanged=[]

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		self._debug("Taking snapshot")
		name=self.inp_name.text()
		name=os.path.basename(name)
		if len(name)>20:
			name=name[0:19]
		functionHelper.take_snapshot(self.wrkDir,name)
		self.optionChanged=[]
		self.updateScreen()

