#!/usr/bin/python3
from . import functionHelper
from . import resolutionHelper
import sys
import os
import tempfile
import subprocess
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QGridLayout,QComboBox,QCheckBox,QToolTip
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper,QSize
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
	"TOOLTIP":_("Set theme, color scheme or pointers"),
	"THEME":_("Desktop theme"),
	"SCHEME":_("Colour scheme"),
	"COLOURS":_("Theme colours"),
	"CURSORTHEME":_("Cursor theme"),
	"CURSORSIZE":_("Cursor size"),
	}

class lookandfeel(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("hotkeys load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-theme')
		self.themesDir="/usr/share/plasma/desktoptheme"
		self.tooltip=i18n.get('TOOLTIP')
		self.index=2
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
		self.config={}
		self.sysConfig={}
		self.wrkFiles=["kdeglobals","kcmimputrc"]
		self.blockSettings={}
		self.wantSettings={"kdeglobals":["General"]}
		self.optionChanged=[]
		self.cursorDesc={}
	#def __init__

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		row,col=(0,0)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._updateConfig)
		self.widgets={}
		config=self.config.get(self.level,{})
		self.config=self.getConfig()

		self.box.addWidget(QLabel(i18n.get("THEME")),0,0,1,1)
		cmbTheme=QComboBox()
		self.widgets.update({'theme':cmbTheme})
		self.box.addWidget(cmbTheme,0,1,1,1)

		self.box.addWidget(QLabel(i18n.get("SCHEME")),1,0,1,1)
		cmbScheme=QComboBox()
		self.widgets.update({'scheme':cmbScheme})
		self.box.addWidget(cmbScheme,1,1,1,1)

		self.box.addWidget(QLabel(i18n.get("CURSORTHEME")),2,0,1,1)
		cmbCursor=QComboBox()
		self.widgets.update({'cursor':cmbCursor})
		cmbCursor.currentIndexChanged.connect(self.updateCursorSizes)
		self.box.addWidget(cmbCursor,2,1,1,1)

		self.box.addWidget(QLabel(i18n.get("CURSORSIZE")),3,0,1,1)
		cmbCursorSize=QComboBox()
		self.widgets.update({'cursorSize':cmbCursorSize})
		self.box.addWidget(cmbCursorSize,3,1,1,1)
		cmbCursorSize.addItem("32")
		cmbCursorSize.addItem("48")
		cmbCursorSize.addItem("64")
		cmbCursorSize.addItem("80")
		cmbCursorSize.addItem("96")
		cmbCursorSize.addItem("112")
		cmbCursorSize.addItem("128")
		cmbCursorSize.currentTextChanged.connect(self.updateCursorIcons)

		self.updateScreen()
		self.updateCursorIcons()
		#self.changes=False
	#def _load_screen

	def updateScreen(self):
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile=wrkFile)
			self.sysConfig.update(systemConfig)
		self.config=self.getConfig()
		theme=""
		for value in self.sysConfig.get("kdeglobals",{}).get("General",[]):
			if value[0]=="Name":
				theme=value[1]
		for cmbDesc in self.widgets.keys():
			cmb=self.widgets.get(cmbDesc,"")
			if isinstance(cmb,QComboBox):
				if cmbDesc=="cursorSize":
					cursorSize=32
					cursorSettings=self.sysConfig.get('kcminputrc',{}).get('Mouse',[])
					for setting in cursorSettings:
						if isinstance(setting,tuple):
							if setting[0]=="cursorSize":
								cursorSize=setting[1]
					if cmb.findText(cursorSize)==-1:
						cmb.insertItem(0,cursorSize)
					cmb.setCurrentText(cursorSize)
				else:
					if cmbDesc=="theme":
						themes=self._getThemeList()
					if cmbDesc=="scheme":
						themes=self._getSchemeList()
					if cmbDesc=="cursor":
						themes=self._getCursorList()
					for theme in themes:
						themeDesc=theme.split("(")[0].replace("(","").rstrip(" ")
						if cmb.findText(themeDesc)==-1:
							if cmbDesc=="cursor":
								#i18n could translate the description, real name needed
								cursorTheme=theme.split("(")[1].replace("(","").replace(")","")
								cursorTheme=cursorTheme.split(" ")[0]
								icon,sizes=self._getPointerImage(cursorTheme)
								if icon:
									cmb.addItem(icon,themeDesc)
								else:
									cmb.addItem(themeDesc)
								self.cursorDesc[themeDesc]=cursorTheme
							else:
								cmb.addItem(themeDesc)
						if "(" in theme and "plasma" in theme.lower():
							cmb.setCurrentText(themeDesc)
		config=self.config.get(self.level,{})
	#def _udpate_screen

	def updateCursorIcons(self):
		cmbSize=self.widgets.get("cursorSize")
		cmbCursors=self.widgets.get("cursor")
		if cmbSize.currentText()=='' or cmbSize.currentText().isdigit()==False:
			cmbSize.setCurrentText("32")
		cmbCursors.setIconSize(QSize(int(cmbSize.currentText()), int(cmbSize.currentText())))
		cmbCursors.adjustSize()
	#def updateSizes

	def updateCursorSizes(self):
		cmbSize=self.widgets.get("cursorSize")
		cmbCursors=self.widgets.get("cursor")
		icon=cmbCursors.itemIcon(cmbCursors.currentIndex())
		maxw=0
		for size in icon.availableSizes():
			if size.width()>maxw:
				maxw=size.width()
		for idx in range(0,cmbSize.count()):
			size=cmbSize.itemText(idx)
			if maxw<int(size) and int(size)>32:	
				cmbSize.model().item(idx).setEnabled(False)
			else:
				cmbSize.model().item(idx).setEnabled(True)
				cmbSize.setCurrentIndex(idx)
	#def updateCursorSizes
		
	def _getPointerImage(self,theme):
		icon=os.path.join("/usr/share/icons",theme,"cursors","left_ptr")
		self._debug("Extracting imgs for icon {}".format(icon))
		if os.path.isfile(icon)==False:
			icon=os.path.join(os.environ.get("HOME",""),".icons",theme,"cursors","left_ptr")
		qicon=""
		sizes=[]
		if os.path.isfile(icon):
			tmpDir=tempfile.TemporaryDirectory()
			cmd=["xcur2png","-q","-c","-","-d",tmpDir.name,icon]
			try:
				subprocess.run(cmd,stdout=subprocess.PIPE)
			except Exception as e:
				print("{}".format(e))
			maxw=0
			img=""
			pixmap=""
			for i in os.listdir(tmpDir.name):
				pixmap=os.path.join(tmpDir.name,i)
				qpixmap=QtGui.QPixmap(pixmap)
				size=qpixmap.size()
				if size.width()>maxw:
					maxw=size.width()
					img=qpixmap
				sizes.append(size)

			if img=="" and pixmap!="":
				img=pixmap
			qicon=QtGui.QIcon(img)
			tmpDir.cleanup()

		return(qicon,sizes)

	def _updateConfig(self,key):
		return
		#	if key in self.kwinMethods:
		#		self._exeKwinMethod(key) 
	
	def writeConfig(self):
		#self.saveChanges('fonts',{"size":size})
		self.optionChanged=[]
		self.refresh=True
		cursorTheme=""
		size=""
		for cmbDesc in self.widgets.keys():
			cmb=self.widgets.get(cmbDesc,"")
			if isinstance(cmb,QComboBox):
				theme=cmb.currentText()
				theme=theme.split("(")[0].strip()
				if cmbDesc=="theme":
					self._setTheme(theme)
				if cmbDesc=="scheme":
					self._setScheme(theme)
				if cmbDesc=="cursor":
					cursorTheme=theme
				if cmbDesc=="cursorSize":
					size=cmb.currentText()
		#Ensure size is applied before theme change
		self._setCursorSize(size)
		self._setCursor(cursorTheme)
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
	#def writeConfig

	def _getThemeList(self):
		availableThemes=[]
		themes=""
		try:
			themes=subprocess.run(["plasma-apply-desktoptheme","--list-themes"],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
		if themes:
			out=themes.stdout.decode()
			for line in out.split("\n"):
				theme=line.strip()
				if theme.startswith("*"):
					availableThemes.append(theme.replace("*","").strip())
		return (availableThemes)
	#def _getThemeList

	def _getSchemeList(self):
		availableSchemes=[]
		schemes=""
		try:
			schemes=subprocess.run(["plasma-apply-colorscheme","--list-schemes"],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
		if schemes:
			out=schemes.stdout.decode()
			for line in out.split("\n"):
				scheme=line.strip()
				if scheme.startswith("*"):
					availableSchemes.append(scheme.replace("*","").strip())
		return (availableSchemes)
	#def _getSchemeList

	def _getCursorList(self):
		availableThemes=[]
		themes=""
		try:
			themes=subprocess.run(["plasma-apply-cursortheme","--list-themes"],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
		if themes:
			out=themes.stdout.decode()
			for line in out.split("\n"):
				theme=line.strip()
				if theme.startswith("*"):
					availableThemes.append(theme.replace("*","").strip())
		return (availableThemes)
	#def _getCursorList

	def _setTheme(self,theme):
		try:
			subprocess.run(["plasma-apply-desktoptheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
	#def _setTheme

	def _setScheme(self,theme):
		try:
			subprocess.run(["plasma-apply-colorscheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
	#def _setScheme

	def _setCursor(self,themeDesc):
		theme=self.cursorDesc.get(themeDesc,themeDesc)
		self._debug("Set cursor theme: {} was {}".format(theme,themeDesc))
		try:
			subprocess.run(["plasma-apply-cursortheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
	#def _setCursor

	def _setCursorSize(self,size):
		self.saveChanges('cursor',{"size":size})
		functionHelper._setKdeConfigSetting("Mouse","cursorSize","{}".format(size),"kcminputrc")
	#def _setCursorSize(self):

