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
from . import functionHelper
QString=type("")

i18n={
	"COLOURS":_("Colours"),
	"FONTS":_("Fonts"),
	"CURSOR":_("Cursor"),
	"AIDS":_("Visual Aids"),
	"SCREEN":_("Screen Options"),
	"HOTKEYS":_("Keyboard Shortcuts"),
	"ACCESSIBILITY":_("Accessibility options"),
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Accessibility configuration"),
	"MENUDESCRIPTION":_("Set accesibility options"),
	"TOOLTIP":_("From here you can activate/deactivate accessibility aids"),
	"HIGHCONTRAST":_("Enable high contrast palette"),
	"INVERTENABLED":_("Invert screen colours"),
	"INVERTWINDOW":_("Invert windows colours"),
	"ANIMATEONCLICK":_("Show animation on button click"),
	"SIZE":_("Font size"),
	"FAMILY":_("Font family"),
	"CURSORTHEME":_("Cursor theme"),
	"CURSORSIZE":_("Cursor size"),
	"FOLLOWPOINTER":_("Always follow the pointer"),
	"SINGLECLICK":_("Only one click for open elements"),
	"SCROLLBARMODE":_("Scrollbar sliding mode"),
	"SHOWDESKTOPGRID":_("Show a grid when moving windows"),
	"ZOOMFISH":_("Activate glass effect with a eyefish effect"),
	"ZOOMGLASS":_("Activate glass effect"),
	"ZOOMNORMAL":_("Zoom desktop"),
	"HOTCORNERS":_("Actions on screen corners"),
	"SYSTEMBELL":_("Acoustic system bell"),
	"FOCUSPOLICY":_("Set the policy focus of windows and applicattions")
	}

class access(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("access Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-accessibility')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=1
		self.enabled=True
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
		systemConfig=functionHelper.getSystemConfig()
		print("****")
		print(systemConfig)
		
		for key,item in config.get('aids',{}).items():
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
				else:
					if key=='scrollbarMode':
						widget=QComboBox()
						widget.addItems([])
						sigmap_run.setMapping(widget,key)
						widget.currentIndexChanged.connect(sigmap_run.map)
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
					hotkey=""
					if optionName in self.kwinMethods:
						print("Kwin method {}".format(optionName))
					elif optionName in self.kaccessSections.keys():
						value=self._getKdeConfigSetting(group=self.kaccessSections.get(optionName),key=optionName)
						hotkey=self._getHotkey(optionName)
					else:
						print("Item not found {}".format(optionName))
					widget=self._getWidgetFromKey(optionName)
					if isinstance(widget,QCheckBox):
						state=False
						if value.lower()=="true":
							state=True
						if not "(" in widget.text(): 
							widget.setText("{} ({})".format(widget.text(),hotkey))
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
						if name in self.kaccessSections:
							self._debug("Setting {} -> {}".format(name,value))
							self._setKdeConfigSetting(group=self.kaccessSections.get(name),key=name,value=value)
						#self._exeKwinMethod(name) 
		self._reloadConfig()
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

	def _reloadConfig(self):
		bus=dbus.SessionBus()
		#return(getDbusObject(,,""))
		kbus=bus.get_object("org.kde.KWin","/KWin")
		methodCall=kbus.reconfigure(dbus_interface='org.kde.KWin')
