#!/usr/bin/python3
from . import functionHelper
from . import resolutionHelper
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTabBar,QTabWidget,QTabBar,QTabWidget,QSlider,QToolTip
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
		self.index=3
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
		self.config={}
		self.sysConfig={}
		self.wrkFiles=["kdeglobals","kcminputrc","konsolerc"]
		self.blockSettings={}
		self.wantSettings={"kdeglobals":["General"]}
		self.optionChanged=[]
	#def __init__

	def _load_screen(self):
		def _showTl():
			sld.setToolTip("{}".format(sld.value()))
			QToolTip.showText(QtGui.QCursor.pos(),"{}".format(sld.value()))

		self.box=QGridLayout()
		self.setLayout(self.box)
		row,col=(0,0)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._updateConfig)
		self.widgets={}
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
		fontSize=config.get('fonts',{}).get('size',"Normal")
		cursorSize=config.get('cursor',{}).get('size',"Normal")

		sld=QSlider(Qt.Horizontal)
		sld.setTickPosition(sld.TicksBothSides)
		sld.setTickInterval(1)
		sld.setMinimum(8)
		sld.setMaximum(120)
		sld.valueChanged.connect(_showTl)		
		#btn=QComboBox()
		#btn.addItem("Normal")
		#btn.addItem("Large")
		#btn.addItem("Extralarge")
		#btn.setCurrentText(fontSize)
		sw_font=True
		self.box.addWidget(QLabel(i18n.get("FONTSIZE")),0,0)
		#self.box.addWidget(btn,0,1)
		self.box.addWidget(sld,0,1)
		#self.widgets.update({"font":btn})
		self.widgets.update({"font":sld})

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
		currentWidth,currentHeight=self.getCurrentResolution()
		btn.addItem("{}".format(currentWidth))
		btn.addItem("1024")
		btn.addItem("1440")
		btn.addItem("1920")
		sw_font=True
		self.box.addWidget(QLabel(i18n.get("RESOLUTION")),2,0)
		self.box.addWidget(btn,2,1)
		self.widgets.update({"res":btn})

		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile=wrkFile)
			self.sysConfig.update(systemConfig)
		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
		fontSize=config.get('fonts',{}).get('size',"11")
		btn=self.widgets.get("font")
		cursorSize=config.get('cursor',{}).get('size',"Normal")
		if btn:
			if isinstance(fontSize,str):
				if fontSize.isalpha():
					fontSize=11
			btn.setValue(int(fontSize))
		btn=self.widgets.get("cursor")
		if btn:
			btn.setCurrentText(cursorSize)
		currentWidth,currentHeight=self.getCurrentResolution()
		btn=self.widgets.get("res")
		if btn:
			btn.setCurrentText(str(currentWidth))
		pass
	#def _udpate_screen

	def _updateConfig(self,key):
		return
		#	if key in self.kwinMethods:
		#		self._exeKwinMethod(key) 
	
	def getCurrentResolution(self):
		rH=resolutionHelper.kscreenDbus()
		return(rH.getCurrentResolution())

	def writeConfig(self):
		for name,wdg in self.widgets.items():
			if name=="font":
				size=wdg.value()
				minSize=size-2
				self._debug("FONTS SIZE {0} to {1}".format(size,self.level))
				self.saveChanges('fonts',{"size":size})
				fontFixed="Hack"
				fontType="Noto Sans"
				fixed="{0},{1},-1,5,50,0,0,0,0,0".format(fontFixed,size)
				font="{0},{1},-1,5,50,0,0,0,0,0".format(fontType,size)
				menufont="{0},{1},-1,5,50,0,0,0,0,0".format(fontType,size)
				smallestreadablefont="{0},{1},-1,5,50,0,0,0,0,0".format(fontType,minSize)
				toolbarfont="{0},{1},-1,5,50,0,0,0,0,0".format(fontType,size)
				functionHelper._setKdeConfigSetting("General","fixed",fixed,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","font",font,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","menuFont",menufont,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","smallestReadableFont",smallestreadablefont,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","toolBarFont",toolbarfont,"kdeglobals")
				functionHelper._setKdeConfigSetting("Appearance","Font",fixed,"Lliurex.profile")
				self._setMozillaFirefoxFonts(size)
			elif name=="cursor":
				value=wdg.currentText()
				size=24
				inc=12
				if value.lower()=="large":
					size+=inc
				if value.lower()=="extralarge":
					size+=inc*2
				self.saveChanges('cursor',{"size":value})
				functionHelper._setKdeConfigSetting("Mouse","cursorSize","{}".format(size),"kcminputrc")
			elif name=="res":
				w=wdg.currentText()
				self.config=self.getConfig()
				currentw=self.config.get(self.level,{}).get("resolution","")
				if currentw!=w:
					if w=="1920":
						h=1080
					elif w=="1440":
						h=900
					elif w=="1024":
						h=768
					else:
						h=int((w*9)/16)
					h=str(h)
					self._debug("Setting resolution to {} {}".format(w,h))
					rH=resolutionHelper.kscreenDbus()
					config=rH.getConfig()
					modeId=rH.getResolutionMode(config,w,h)
					if modeId:
						rH.setResolution(config,modeId)

					self.saveChanges('resolution',w)
		self.optionChanged=[]
		self.refresh=True
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
	#def writeConfig

	def _setMozillaFirefoxFonts(self,size):
		size+=7 #Firefox font size is smallest.
		mozillaDir=os.path.join(os.environ.get('HOME',''),".mozilla/firefox")
		for mozillaF in os.listdir(mozillaDir):
			self._debug("Reading MOZILLA {}".format(mozillaF))
			fPath=os.path.join(mozillaDir,mozillaF)
			if os.path.isdir(fPath):
				self._debug("Reading DIR {}".format(mozillaF))
				if "." in mozillaF:
					self._debug("Reading DIR {}".format(mozillaF))
					prefs=os.path.join(mozillaDir,mozillaF,"prefs.js")
					if os.path.isfile(prefs):
						with open(prefs,'r') as f:
							lines=f.readlines()
						newLines=[]
						for line in lines:
							if line.startswith('user_pref("font.minimum-size.x-unicode"'):
								continue
							elif line.startswith('user_pref("font.minimum-size.x-western"'):
								continue
							newLines.append(line)
						line='user_pref("font.minimum-size.x-western", {});\n'.format(size)
						newLines.append(line)
						line='user_pref("font.minimum-size.x-unicode", {});\n'.format(size)
						newLines.append(line)
						self._debug("Writting MOZILLA {}".format(mozillaF))
						with open(os.path.join(mozillaDir,mozillaF,"prefs.js"),'w') as f:
							f.writelines(newLines)
	#def _setMozillaFirefoxFonts
