#!/usr/bin/python3
from . import functionHelper
from . import resolutionHelper
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTabBar,QTabWidget,QTabBar,QTabWidget,QSlider,QToolTip,QListWidget,QFontDialog,QGroupBox,QListView
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper,QEvent
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import json
import dbus,dbus.service,dbus.exceptions
QString=type("")

i18n={
	"ACCESSIBILITY":_("Font options"),
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Font configuration"),
	"MENUDESCRIPTION":_("Modify system fonts"),
	"TOOLTIP":_("Customize the system fonts"),
	"FONTSIZE":_("Font size"),
	"FAMILY":_("Font family"),
	"CURSORTHEME":_("Cursor theme"),
	"CURSORSIZE":_("Cursor size")
	}

class fonts(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("fonts load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-font')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=4
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
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile=wrkFile)
			self.sysConfig.update(systemConfig)
		kdevalues=self.sysConfig.get('kdeglobals',{}).get('General',[])
		font=''
		for value in kdevalues:
			if isinstance(value,tuple):
				if value[0]=='font':
					font=value[1]
					break
		dlgFont=QFontDialog(font)
		#Embed in window
		dlgFont.setWindowFlags(Qt.Widget)
		dlgFont.setOptions(dlgFont.NoButtons)
		#dlgFont.currentFontChanged.connect(self._dlgChange)
		#Customize widget
		for chld in dlgFont.findChildren(QGroupBox):
			for groupChld in chld.findChildren(QCheckBox):
				chld.hide()
				break

		row,col=(0,0)
		self.box.addWidget(dlgFont)
		#sigmap_run=QSignalMapper(self)
		#sigmap_run.mapped[QString].connect(self._updateConfig)
		self.widgets={}
		self.widgets.update({"font":dlgFont})
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		self.config=self.getConfig()
		kdevalues=self.sysConfig.get('kdeglobals',{}).get('General',[])
		for value in kdevalues:
			if isinstance(value,tuple):
				if value[0]=='font':
					font=value[1]
					break
		qfont=QtGui.QFont(font)
		dlgFont=self.widgets.get('font')
		dlgFont.setCurrentFont(font)
		#fix listview selections
		style=font.split(",")[-1]
		for chld in dlgFont.findChildren(QListView):
			sw_alpha=True
			model=chld.model()
			if style.isalpha():
				for row in range(model.rowCount()):
					index=model.index(row,0)
					data=model.data(index)
					if data==style:
						chld.setCurrentIndex(index)
						break
					elif data.isalpha==False:
						sw_alpha=False
						break
				if sw_alpha==False:
					break
			chld.scrollTo(chld.currentIndex())
		for chld in dlgFont.findChildren(QComboBox):
			chld.setCurrentIndex(1)
		config=self.config.get(self.level,{})
	#def _udpate_screen

	def _updateConfig(self,key):
		return
		#	if key in self.kwinMethods:
		#		self._exeKwinMethod(key) 
	
	def writeConfig(self):
		for name,wdg in self.widgets.items():
			if name=="font":
				qfont=wdg.currentFont()
				font=qfont.toString()
				minfont=font
				size=qfont.pointSize()
				minSize=size-2
				self._debug("FONT: {}".format(size))
				self.saveChanges('fonts','{}'.format(font))
				fontFixed="Hack"
				fixed="{0},{1},-1,5,50,0,0,0,0,0".format(fontFixed,size)
				if size>8:
					qfont.setPointSize(size-2)
					minFont=qfont.toString()
				functionHelper._setKdeConfigSetting("General","fixed",fixed,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","font",font,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","menuFont",font,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","smallestReadableFont",minFont,"kdeglobals")
				functionHelper._setKdeConfigSetting("General","toolBarFont",font,"kdeglobals")
				functionHelper._setKdeConfigSetting("Appearance","Font",fixed,"Lliurex.profile")
				self._setMozillaFirefoxFonts(size)
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
