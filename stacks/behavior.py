#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTabBar,QTabWidget,QTabBar,QTabWidget
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
from . import functionHelper
import gettext
_ = gettext.gettext
QString=type("")

i18n={
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Desktop behaviour"),
	"MENUDESCRIPTION":_("Configure how desktop works"),
	"TOOLTIP":_("Set many options related with desktop behavior"),
	"FOCUSCLICK":_("Click to focus"),
	"FOCUSFOLLOW":_("Focus follows pointer"),
	"SINGLECLICK":_("Only one click for open elements"),
	"SCROLLBARLEFTCLICKNAVIGATESBYPAGE":_("Click on scrollbar moves to position"),
	"SCROLLBARMODE":_("Scrollbar sliding mode"),
	"GRIDONMOVE":_("Show a grid when moving windows"),
	"HOTCORNERS":_("Actions on top left screen corner"),
	"RESOLUTION":_("Set screen resolution"),
	"FOCUSPOLICY":_("Set the policy focus of windows and applicattions")
	}

class behavior(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("behavior load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('application-x-desktop')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=1
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
		self.level='user'
		self.bus=None
		self.sysConfig={}
		self.config={}
		self.wrkFiles=["kdeglobals","kwinrc"]
		self.wantSettings={"kwinrc":["FocusPolicy"]}
		self.blockSettings={}
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
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile)
			self.sysConfig.update(systemConfig)
			for kfile,sections in systemConfig.items():
				for section,settings in sections.items():
					for setting in settings:
						(name,data)=setting
						want=self.wantSettings.get(kfile,[])
						block=self.blockSettings.get(kfile,[])
						if name in block or (len(want)>0 and name not in want):
							continue
						desc=i18n.get(name.upper(),name)
						lbl=QLabel(desc)
						if name=='FocusPolicy':
							btn=QComboBox()
							btn.addItem(i18n.get("FOCUSCLICK"))
							btn.addItem(i18n.get("FOCUSFOLLOW"))
						elif (data.lower() in ("true","false")) or (data==''):
							btn=QCheckBox(desc)
							state=False
							if data.lower()=="true":
								state=True
							btn.setChecked(state)
						self.box.addWidget(btn)
						self.widgets.update({name:btn})

		self.updateScreen()
		return
		self.config=self.getConfig(level=self.level)
		config=self.config.get(self.level,{})
		for key,item in config.get('desktopbehaviour',{}).items():
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
				elif key=='focusPolicy':
					self.box.addWidget(QLabel(i18n.get('FOCUSPOLICY')))
					widget=QComboBox()
					widget.addItems([i18n.get("FOCUSCLICK"),i18n.get("FOCUSFOLLOW")])
					sigmap_run.setMapping(widget,key)
					widget.currentIndexChanged.connect(sigmap_run.map)
				elif key=='resolution':
					self.box.addWidget(QLabel(i18n.get('RESOLUTION')))
					widget=QComboBox()
					widget.addItems([])
					sigmap_run.setMapping(widget,key)
					widget.currentIndexChanged.connect(sigmap_run.map)
				elif key=='hotCorners':
					self.box.addWidget(QLabel(i18n.get('HOTCORNERS')))
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

