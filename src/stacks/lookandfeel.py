#!/usr/bin/python3
from . import functionHelper
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTabBar,QTabWidget,QTabBar,QTabWidget
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import json
import dbus,dbus.service,dbus.exceptions
QString=type("")

i18n={
	"ACCESSIBILITY":_("Look&Feel options"),
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Look&Feel configuration"),
	"MENUDESCRIPTION":_("Modify appearence settings"),
	"TOOLTIP":_("From here you can set hotkeys for launch apps"),
	"FONTSIZE":_("Font size"),
	"FAMILY":_("Font family"),
	"CURSORTHEME":_("Cursor theme"),
	"CURSORSIZE":_("Cursor size"),
	"RESOLUTION":_("Set resolution")
	}

class lookandfeel(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("hotkeys load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-theme')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=1
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
		self.level='user'
		self.config={}
		self.sysConfig={}
		self.wrkFiles=["kdeglobals","kcminputrc"]
		self.blockSettings={}
		self.wantSettings={"kdeglobals":["General"]}
		self.optionChanged=[]
	#def __init__

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		row,col=(0,0)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._updateConfig)
		self.widgets={}
		self.level='system'
		self.refresh=True
		self.config=self.getConfig(level=self.level)
		config=self.config.get(self.level,{})
		fontSize=config.get('fonts',{}).get('size',"Normal")
		cursorSize=config.get('cursor',{}).get('size',"Normal")

		btn=QComboBox()
		btn.addItem("Normal")
		btn.addItem("Large")
		btn.addItem("Extralarge")
		btn.setCurrentText(fontSize)
		sw_font=True
		self.box.addWidget(QLabel(i18n.get("FONTSIZE")),0,0)
		self.box.addWidget(btn,0,1)
		self.widgets.update({"font":btn})

		btn=QComboBox()
		btn.addItem("Normal")
		btn.addItem("Large")
		btn.addItem("Extralarge")
		btn.setCurrentText(cursorSize)
		sw_font=True
		self.box.addWidget(QLabel(i18n.get("CURSORSIZE")),1,0)
		self.box.addWidget(btn,1,1)
		self.widgets.update({"cursor":btn})

		btn=QComboBox()
		btn.addItem("1024")
		btn.addItem("1440")
		btn.addItem("HD")
		sw_font=True
		self.box.addWidget(QLabel(i18n.get("RESOLUTION")),2,0)
		self.box.addWidget(btn,2,1)
		self.widgets.update({"res":btn})

		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile=wrkFile)
			self.sysConfig.update(systemConfig)
		"""

		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile)
			self.sysConfig.update(systemConfig)
			for kfile,sections in systemConfig.items():
				want=self.wantSettings.get(kfile,[])
				block=self.blockSettings.get(kfile,[])
				sw_font=False
				for section,settings in sections.items():
					if section in block and len(want)==0:
						continue
					for setting in settings:
						(name,data)=setting
						if name in block or (len(want)>0 and name not in want and section not in want):
							continue
						desc=i18n.get(name.upper(),name)
						lbl=QLabel(desc)
						#if (data.lower() in ("true","false")) or (data==''):
						if (isinstance(data,str)):
							#btn=QCheckBox(desc)
							if ("font" in name.lower()) or ("fixed" in name.lower()):
								if sw_font==True:
									continue
								btn=QComboBox()
								btn.addItem("Normal")
								btn.addItem("Large")
								btn.addItem("Extralarge")
								sw_font=True
								self.box.addWidget(QLabel("Font Size"),row,col)
								col+=1
								if col==2:
									row+=1
									col=0
							elif ("size") in name.lower():
								btn=QComboBox()
								btn.addItem("Normal")
								btn.addItem("Large")
								btn.addItem("Extralarge")
								sw_font=True
								self.box.addWidget(QLabel("Cursor Size"),row,col)
								col+=1
								if col==2:
									row+=1
									col=0

							else:
								btn=QPushButton(desc)
								btn.setStyleSheet(functionHelper.cssStyle())
								btn.setAutoDefault(False)
								btn.setDefault(False)
								btn.setCheckable(True)
								state=False
								#if  data in ("true","false"):
								if data.lower()=="true" or data.lower()=="focusfollowsmouse":
									state=True
								btn.setChecked(state)
						self.widgets.update({name:btn})
						self.box.addWidget(btn,row,col)
						col+=1
						if col==2:
							row+=1
							col=0
		"""
		"""
		self.config=self.getConfig(level=self.level)
		config=self.config.get(self.level,{})
		lookandfeelSections=['colours','fonts','cursor']
		for section in lookandfeelSections:
			for key,item in config.get(section,{}).items():
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
					elif key=='size':
						self.box.addWidget(QLabel(i18n.get('SIZE')))
						widget=QComboBox()
						widget.addItems(["12","13","14","15","16","17","18","19","20"])
						sigmap_run.setMapping(widget,key)
						widget.currentIndexChanged.connect(sigmap_run.map)
					elif key=='family':
						self.box.addWidget(QLabel(i18n.get('FAMILY')))
						widget=QComboBox()
						widget.addItems([])
						sigmap_run.setMapping(widget,key)
						widget.currentIndexChanged.connect(sigmap_run.map)
					elif key=='cursorSize':
						self.box.addWidget(QLabel(i18n.get('CURSORSIZE')))
						widget=QComboBox()
						widget.addItems(["Normal","Large","Extralarge"])
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
					#self.widgets[key]=widget
					#self.box.addWidget(widget)
					self.widgets.update({name:btn})
					self.box.addWidget(btn,row,col)
					col+=1
					if col==2:
						row+=1
						col=0
			"""
		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		pass
	#def _udpate_screen

	def _updateConfig(self,key):
		return
		#	if key in self.kwinMethods:
		#		self._exeKwinMethod(key) 

	def writeConfig(self):
		for name,wdg in self.widgets.items():
			if name=="font":
				value=wdg.currentText()
				size=11
				minSize=9
				inc=2
				if value.lower()=="large":
					size+=inc
					minSize+=inc
				if value.lower()=="extralarge":
					size+=inc*2
					minSize+=inc*2
				self.saveChanges('fonts',{"size":value})
				fixed="Hack,{0},-1,5,50,0,0,0,0,0".format(size)
				font="Noto Sans,{0},-1,5,50,0,0,0,0,0".format(size)
				menufont="Noto Sans,{0},-1,5,50,0,0,0,0,0".format(size)
				smallestreadablefont="Noto Sans,{0},-1,5,50,0,0,0,0,0".format(minSize)
				toolbarfont="Noto Sans,{0},-1,5,50,0,0,0,0,0".format(size)
				functionHelper._setKdeConfigSetting("General","fixed",fixed,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","font",font,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","menuFont",menufont,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","smallestReadableFont",smallestreadablefont,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","toolBarFont",toolbarfont,"kdeglobals")
			elif name=="cursor":
				value=wdg.currentText()
				size=24
				inc=12
				if value.lower()=="large":
					size+=inc
				if value.lower()=="extralarge":
					size+=inc*2
				self.saveChanges('cursor',{"size":value})
			elif name=="res":
				self._debug("Not implemented")
		self.optionChanged=[]
		return

