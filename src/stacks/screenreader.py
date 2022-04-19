#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTabBar,QTabWidget,QTabBar,QTabWidget
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import json
import subprocess
import dbus,dbus.service,dbus.exceptions
QString=type("")

i18n={
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Orca settings"),
	"MENUDESCRIPTION":_("Orca related options"),
	"TOOLTIP":_("Some options related with Orca"),
	"LAUNCH":_("Hotkey for launching Orca"),
	"RESTART":_("Hotkey for restarting Orca"),
	"IMPORT":_("Import Orca settings")
	}

class screenreader(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-text-to-speech')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=11
		self.enabled=False
		self.defaultRepos={}
		self.changed=[]
		self.level='user'
		self.bus=None
		self.config={}
		#self.kwinMethods=self._getKwinMethods()
		self.kwinMethods={}
		self.kaccessSections={"SystemBell":"Bell","invertEnabled":"Plugins","SingleClick":"KDE"}
		self.fileSections={"Bell":"kaccessrc","Plugins":"kwinrc","KDE":"kdeglobals"}
		self.optionChanged=[]
	#def __init__

	def _load_screen(self):
		self.box=QVBoxLayout()
		self.setLayout(self.box)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._updateConfig)
		self.widgets={}
		self.level='user'
		self.refresh=True
		self.config=self.getConfig(level=self.level)
		config=self.config.get(self.level,{})
		lbl_launch=QLabel(i18n.get("LAUNCH"))
		btn_launch=QPushButton()
		lbl_restart=QLabel(i18n.get("RESTART"))
		btn_restart=QPushButton()
		lbl_import=QLabel(i18n.get("IMPORT"))
		btn_import=QPushButton()
		self.box.addWidget(lbl_launch)
		self.box.addWidget(btn_launch)
		self.box.addWidget(lbl_restart)
		self.box.addWidget(btn_restart)
		self.box.addWidget(lbl_import)
		self.box.addWidget(btn_import)
		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		pass
	#def _udpate_screen

	def _updateConfig(self,key):
		widget=self._getWidgetFromKey(key)
		self.setChanged(True)
		section=self._getSectionFromKey(key)
		if section:
			if isinstance(widget,QCheckBox):
				value=str(widget.isChecked()).lower()
			elif isinstance(widget,QLineEdit):
				value=widget.text()
			self.config[self.level][section].update({key:value})
		self.optionChanged.append(key)
		self._debug("Changed: {}".format(key))
		#	if key in self.kwinMethods:
		#		self._exeKwinMethod(key) 

	def writeConfig(self):
		for section,option in self.config.get(self.level,{}).items():
			if isinstance(option,dict):
				for name,value in option.items():
					if name in self.optionChanged:
						if name in self.kaccessSections:
							self._debug("Setting {} -> {}".format(name,value))
							self._setKdeConfigSetting(group=self.kaccessSections.get(name),key=name,value=value)
						#self._exeKwinMethod(name) 
		self.optionChanged=[]

	def _getSectionFromKey(self,key):
		sec=''
		for section,option in self.config.get(self.level,{}).items():
			if isinstance(option,dict):
				if key in option.keys():
					sec=section
					break
		return(sec)

	def _getWidgetFromKey(self,key):
		return(self.widgets.get(key,''))

	
	def _connect(self):
		bus=None
		try:
			bus=dbus.SessionBus()
		except Exception as e:
			bus=None
			print("Could not get session bus: %s\nAborting"%e)
		return(bus)

	def _getKwinMethods(self):
		relevantMethods=[]
		bus=dbus.SessionBus()
		#return(getDbusObject(,,""))
		kbus=bus.get_object("org.kde.kglobalaccel","/component/kwin")
		interface=dbus.Interface(kbus,"org.kde.kglobalaccel.Component")
		#method=interface.get_dbus_method("org.kde.kglobalaccel.Component.allShortcutInfos")
		method=interface.get_dbus_method("allShortcutInfos")
		result=method()
		for dbusRes in result:
			relevantMethods.append(dbusRes[0])
		return(relevantMethods)

	def _exeKwinMethod(self,method):
		bus=dbus.SessionBus()
		kbus=bus.get_object("org.kde.kglobalaccel","/component/kwin")
		interface=dbus.Interface(kbus,"org.kde.kglobalaccel.Component")
		methodCall=interface.get_dbus_method("invokeShortcut")
		self._debug("Calling {}".format(method))
		methodCall(method)

	def _disableKwinMethod(self,method):
		pass

	def _getKdeConfigSetting(self,group,key,kfile="kaccessrc"):
		#kfile=kaccessrc
		kfile=self.fileSections.get(group,'kaccesrc')
		self._debug("Reading value {} from {}".format(key,kfile))
		cmd=["kreadconfig5","--file",os.path.join(os.environ['HOME'],".config",kfile),"--group",group,"--key",key]
		ret='false'
		try:
			ret=subprocess.check_output(cmd,universal_newlines=True).strip()
		except Exception as e:
			print(e)
		self._debug("Read value: {}".format(ret))
		return(ret)

	def _setKdeConfigSetting(self,group,key,value,kfile="kaccessrc"):
		#kfile=kaccessrc
		kfile=self.fileSections.get(group,'kaccesrc')
		self._debug("Writing value {} from {} -> {}".format(key,kfile,value))
		cmd=["kwriteconfig5","--file",os.path.join(os.environ['HOME'],".config",kfile),"--group",group,"--key",key,"{}".format(value)]
		ret='false'
		try:
			ret=subprocess.check_output(cmd,universal_newlines=True).strip()
		except Exception as e:
			print(e)
		self._debug("Write value: {}".format(ret))
		return(ret)

	def _getHotkey(self,key):
		group="kwin"
		if key=='invertEnabled':
			key="Invert"
		kfile="kglobalshortcutsrc"
		cmd=["kreadconfig5","--file",os.path.join(os.environ['HOME'],".config",kfile),"--group",group,"--key",key]
		ret='false'
		try:
			ret=subprocess.check_output(cmd,universal_newlines=True).strip()
		except Exception as e:
			print(e)
		if "," in ret:
			val=ret.split(',')
			ret=val[0]
		self._debug("Hotkey value: {}".format(ret))
		return(ret)
