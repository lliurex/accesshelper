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
	"HOTKEYS":_("Keyboard Shortcuts"),
	"ACCESSIBILITY":_("hotkeys options"),
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Hotkeys configuration"),
	"MENUDESCRIPTION":_("Set hotkeys for launch applications"),
	"TOOLTIP":_("From here you can set hotkeys for launch apps"),
	"NEXTWINDOW":_("Go to next window"),
	"PREVWINDOW":_("Go to previous window"),
	"CLOSEWINDOW":_("Close window"),
	"LAUNCHCOMMAND":_("Open launch menu"),
	"SHOWDESKTOP":_("Show desktop")
	}

class hotkeys(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("hotkeys load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('input-keyboard')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=1
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
		self.level='user'
		self.bus=None
		self.config={}
		self.kaccessSections={"SingleClick":"KDE","ScrollbarLeftClickNavigatesByPage":"KDE"}
		self.fileSections={"KDE":"kdeglobals"}
		#self.kwinMethods=self._getKwinMethods()
		self.kwinMethods={}
		self.optionChanged=[]
	#def __init__

	def _load_screen(self):
		self.box=QVBoxLayout()
		self.tabBar=QTabWidget()
		self.box.addWidget(self.tabBar,0)
		self.setLayout(self.box)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._updateConfig)
		self.widgets={}
		self.level='user'
		self.refresh=True
		self.config=self.getConfig(level=self.level)
		config=self.config.get(self.level,{})
		for key,item in config.get('hotkeys',{}).items():
			if key.upper() in i18n.keys():
				desc=i18n.get(key.upper())
			else:
				desc=key
			widget=None
			if (isinstance(item,str)):
				if item in ["true","false"]:
					widget=QCheckBox(desc)
					sigmap_run.setMapping(widget,key)
					widget.stateChanged.connect(sigmap_run.map)
				elif key=='nextWindow':
					self.box.addWidget(QLabel(i18n.get('NEXTWINDOW')))
					hotkey=self._getHotkey("Walk Through Windows")
					widget=QPushButton(hotkey)
					sigmap_run.setMapping(widget,key)
					widget.pressed.connect(sigmap_run.map)
				elif key=='prevWindow':
					self.box.addWidget(QLabel(i18n.get('PREVWINDOW')))
					hotkey=self._getHotkey("Walk Through Windows (Reverse)")
					widget=QPushButton(hotkey)
					sigmap_run.setMapping(widget,key)
					widget.pressed.connect(sigmap_run.map)
				elif key=='closeWindow':
					self.box.addWidget(QLabel(i18n.get('CLOSEWINDOW')))
					hotkey=self._getHotkey("Window Close")
					widget=QPushButton(hotkey)
					sigmap_run.setMapping(widget,key)
					widget.pressed.connect(sigmap_run.map)
				elif key=='showDesktop':
					self.box.addWidget(QLabel(i18n.get('SHOWDESKTOP')))
					hotkey=self._getHotkey("Show Desktop")
					widget=QPushButton(hotkey)
					sigmap_run.setMapping(widget,key)
					widget.pressed.connect(sigmap_run.map)
				elif key=='launchCommand':
					self.box.addWidget(QLabel(i18n.get('LAUNCHCOMMAND')))
					widget=QPushButton()
					sigmap_run.setMapping(widget,key)
					widget.pressed.connect(sigmap_run.map)

				else:
					widget=QLineEdit()
					sigmap_run.setMapping(widget,key)
					widget.editingFinished.connect(sigmap_run.map)
			elif (isinstance(item,list)):
				print("{} -> List".format(item))
			elif (isinstance(item,dict)):
				print("{} -> Dict".format(item))
			if widget:
				self.widgets[key]=widget
				self.box.addWidget(widget)
		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		self.level='user'
		self.refresh=True
		self.config=self.getConfig(level=self.level)
		for section,option in self.config.get(self.level,{}).items():
			if (isinstance(option,dict)):
				for optionName,value in option.items():
####				if optionName in self.kwinMethods:
####					print("Kwin method {}".format(optionName))
####				else:
####					print("Item not found {}".format(optionName))
					widget=self._getWidgetFromKey(optionName)
					if isinstance(widget,QCheckBox):
						state=False
						if value.lower()=="true":
							state=True
						widget.setChecked(state)
					if isinstance(widget,QLineEdit):
						widget.setText(value)
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
						print(name)
						self._exeKwinMethod(name) 
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
