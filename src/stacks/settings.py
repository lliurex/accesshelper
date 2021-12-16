#!/usr/bin/python3
import sys
import os
import shutil
from PySide2.QtWidgets import QApplication,QLineEdit, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
import subprocess
import tempfile
import gettext
from . import functionHelper
_ = gettext.gettext
QString=type("")

i18n={
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Manage application"),
	"MENUDESCRIPTION":_("Configure some options"),
	"TOOLTIP":_("Set config level, default template.."),
	"AUTOSTART":_("Autostart enabled for user"),
	"DISABLEAUTOSTART":_("Autostart disabled for user")
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
		self.config={}
		self.widgets={}
		self.wrkDirs=["/usr/share/accesshelper/profiles","/usr/share/accesshelper/default",os.path.join(os.environ.get('HOME'),".config/accesshelper/profiles")]
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
		self.widgets.update({self.cmb_level:'config'})
		lbl_help=QLabel("")
		lbl_help.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_help,1,0,1,2)
		box.addWidget(QLabel(_("Session settings")),2,0,1,2,Qt.AlignTop)
		#self.chk_startup=QCheckBox(_("Launch at startup"))
		#box.addWidget(self.chk_startup,3,0,1,2)
		chk_template=QCheckBox(_("Load template on start"))
		box.addWidget(chk_template,3,0,1,1,Qt.AlignTop)
		self.widgets.update({chk_template:'startup'})
		cmb_template=QComboBox()
		self.widgets.update({cmb_template:'profile'})
		box.addWidget(cmb_template,3,1,1,1,Qt.AlignTop)
		box.setRowStretch(0,1)
		box.setRowStretch(1,0)
		box.setRowStretch(2,0)
		box.setRowStretch(3,2)

		for wrkDir in self.wrkDirs:
			if os.path.isdir(wrkDir):
				for f in os.listdir(wrkDir):
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
		self.cmb_level.setCurrentIndex(idx)
	#	self.updateScreen()
	#def fakeUpdate

	def updateScreen(self,level=None):
		config=self.getConfig(level)
		level=self.level
		profile=''
		if level in config.keys():
			profile=config[level].get('profile','')
		startup=config[level].get('startup',False)
		if startup:
			if str(startup).lower()=='true':
				startup=True
			else:
				startup=False
		for widget,desc in self.widgets.items():
			if desc=="startup":
				widget.setChecked(startup)
			elif desc=="profile":
				widget.setCurrentText(profile)
			elif desc=="config":
				if level=="user":
					idx=0
				elif level=="system":
					idx=1
				elif level=="n4d":
					idx=2
				
				widget.setCurrentIndex(idx)
	#def _udpate_screen

	def _updateConfig(self,key):
		pass
	#def _updateConfig

	def writeConfig(self):
		startWdg=None
		profile=''
		for widget,desc in self.widgets.items():
			if desc=="startup":
				startWdg=widget
			if isinstance(widget,QCheckBox):
				value=widget.isChecked()
				if value:
					value="true"
				else:
					value="false"
			elif isinstance(widget,QComboBox):
				if desc=="config":
					value=widget.currentIndex()
					if value==0:
						value="user"
					elif value==1:
						value="system"
					elif value==2:
						value="n4d"
				else:
					value=widget.currentText()
					profile=value
			self.saveChanges(desc,value)
		if startWdg:
			if startWdg.isChecked():
				self._setAutostart(profile)
			else:
				self._removeAutostart(profile)
		f=open("/tmp/accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
	#def writeConfig

	def _setAutostart(self,profile):
		if profile:
			tmpHdl,tmpF=tempfile.mkstemp()
			tmpf=open(tmpF,'w')
			with open("/usr/share/accesshelper/helper/accesshelper-profiler.desktop","r") as f:
				lines=f.readlines()
				for line in lines:
					if line.startswith("Exec="):
						line=line.replace("%u",profile)
					tmpf.write(line)
			tmpf.close()
			destPath=os.path.join(os.environ.get("HOME"),".config/autostart/accesshelper-profiler.desktop")
			shutil.copy(tmpF,destPath)
			self.showMsg("{} {}".format(i18n.get("AUTOSTART"),os.environ.get("USER")))
	#def _setAutostart

	def _removeAutostart(self,profile):
		destPath=os.path.join(os.environ.get("HOME"),".config/autostart/accesshelper-profiler.desktop")
		if os.path.isfile(destPath):
			os.remove(destPath)
			self.showMsg("{} {}".format(i18n.get("DISABLEAUTOSTART"),os.environ.get("USER")))
	#def _removeAutostart
