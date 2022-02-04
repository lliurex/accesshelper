#!/usr/bin/python3
from . import functionHelper
from . import resolutionHelper
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTabBar,QTabWidget,QTabBar,QTabWidget,QSlider,QToolTip,QListWidget
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
	"THEME":_("Desktop theme"),
	"COLOURS":_("Theme colours"),
	"CURSORTHEME":_("Cursor theme"),
	"CURSORSIZE":_("Cursor size"),
	"RESOLUTION":_("Set resolution"),
	}

class lookandfeel(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("hotkeys load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-theme')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=7
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
		self.box=QGridLayout()
		self.setLayout(self.box)
		row,col=(0,0)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._updateConfig)
		self.widgets={}
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile=wrkFile)
			self.sysConfig.update(systemConfig)
		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
	#def _udpate_screen

	def _updateConfig(self,key):
		return
		#	if key in self.kwinMethods:
		#		self._exeKwinMethod(key) 
	
	def writeConfig(self):
		#self.saveChanges('fonts',{"size":size})
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
