#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication,QLineEdit, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
from . import functionHelper
_ = gettext.gettext
QString=type("")

i18n={
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Manage application"),
	"MENUDESCRIPTION":_("Configure some options"),
	"TOOLTIP":_("Set config level, default template.."),
	}

class settings(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("settings Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('systemsettings')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=6
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.config={}
		self.wrkDir="/usr/share/accesshelper/profiles"
		self.optionChanged=[]
	#def __init__

	def _load_screen(self):
		def _change_osh():
			idx=self.cmb_level.currentIndex()
			if idx==0:
				lbl_help.setText(_("The config will be applied per user"))
			elif idx==1:
				lbl_help.setText(_("The config will be applied to all users"))
			elif idx==2:
				lbl_help.setText(_("The config will be applied to all users and clients"))
			self.fakeUpdate()
		box=QGridLayout()
		lbl_txt=QLabel(_("Choose the config level that should use the app"))
		box.addWidget(lbl_txt,0,0,1,1)
		self.cmb_level=QComboBox()
		self.cmb_level.addItem(_("User"))
		self.cmb_level.addItem(_("System"))
		self.cmb_level.addItem(_("N4d"))
		self.cmb_level.activated.connect(_change_osh)
		self.cmb_level.setFixedWidth(100)
		box.addWidget(self.cmb_level,0,1,1,1)
		lbl_help=QLabel("")
		lbl_help.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_help,1,0,1,2)
		box.addWidget(QLabel(_("Session settings")),2,0,1,2,Qt.AlignTop)
		#self.chk_startup=QCheckBox(_("Launch at startup"))
		#box.addWidget(self.chk_startup,3,0,1,2)
		chk_template=QCheckBox(_("Load template on start"))
		box.addWidget(chk_template,3,0,1,1,Qt.AlignTop)
		cmb_template=QComboBox()
		box.addWidget(cmb_template,3,1,1,1,Qt.AlignTop)
		box.setRowStretch(0,1)
		box.setRowStretch(1,0)
		box.setRowStretch(2,0)
		box.setRowStretch(3,2)
		if os.path.isdir(self.wrkDir):
			for f in os.listdir(self.wrkDir):
				cmb_template.addItem("{}".format(f))
			cmb_template.setCurrentText("default")
		self.setLayout(box)
		_change_osh()
		self.updateScreen()
		return(self)
	#def _load_screen

	def fakeUpdate(self):
		idx=self.cmb_level.currentIndex()
		level='user'
		if idx==0:
			level='user'
		elif idx==1:
			level='system'
		elif idx==2:
			level='n4d'
		config=self.getConfig(level)
		close=False
		if level in config.keys():
			close=config[level].get('close',False)
		if close:
			if str(close).lower()=='true':
				close=True
			else:
				close=False
		try:
			self.chk_close.setChecked(close)
		except:
			pass
		startup=config[level].get('startup',False)
		if startup:
			if str(startup).lower()=='true':
				startup=True
			else:
				startup=False
		try:
			self.chk_startup.setChecked(startup)
		except:
			pass

	#def fakeUpdate

	def updateScreen(self):
		pass
	#def _udpate_screen

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		pass

