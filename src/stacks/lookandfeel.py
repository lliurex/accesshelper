#!/usr/bin/python3
from . import libaccesshelper
import sys
import os,shutil
import tempfile
import subprocess
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QGridLayout,QComboBox,QCheckBox,QToolTip,QScrollArea
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
	"CONFIG":_("Look&Feel"),
	"DESCRIPTION":_("Look&Feel"),
	"MENUDESCRIPTION":_("Modify appearence settings"),
	"TOOLTIP":_("Set theme, color scheme or pointers"),
	"THEME":_("Desktop theme"),
	"SCHEME":_("Color scheme"),
	"COLORS":_("Theme colors"),
	"BACKGROUND":_("Background color"),
	"BACKIMG":_("Desktop background"),
	"CURRENTBKG":_("Current background"),
	"CURSORSIZE":_("Cursor size"),
	"CURSORTHEME":_("Cursor theme"),
	"SCALE":_("Widget size"),
	"XSCALE":_("Scale factor"),
	"MAXIMIZE":_("Run apps maximized"),
	"WHITE":_("White"),
	"RED":_("Red"),
	"BLUE":_("Blue"),
	"GREEN":_("Green"),
	"YELLOW":_("Yellow"),
	"BLACK":_("Black"),
	"TRUE":_("Enabled"),
	"FALSE":_("Disabled"),
	}

class lookandfeel(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("hotkeys load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-theme')
		self.themesDir="/usr/share/plasma/desktoptheme"
		self.tooltip=i18n.get('TOOLTIP')
		self.index=2
		self.enabled=True
		self.changed=[]
		self.config={}
		self.plasmaConfig={}
		self.wrkFiles=["kdeglobals","kcmimputrc"]
		self.blockSettings={}
		self.wantSettings={"kdeglobals":["General","KScreen"]}
		self.optionChanged=[]
		self.imgFile=""
		self.bkgIconSize=96
		self.cursorDesc={}
		self.cursorThemes={}
		self.accesshelper=libaccesshelper.accesshelper()
	#def __init__

	def _load_screen(self):
		self.box=QGridLayout()
		box=QGridLayout()
		wdg=QWidget()
		wdg.setLayout(box)
		self.setLayout(self.box)
		row,col=(0,0)
		scr=QScrollArea()
		self.box.addWidget(scr)
		self.widgets={}
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
		if config.get("background"):
			self.imgFile=config.get("background")

		box.addWidget(QLabel(i18n.get("THEME")),0,0,1,1)
		cmbTheme=QComboBox()
		self.widgets.update({'theme':cmbTheme})
		box.addWidget(cmbTheme,0,1,1,1)

		box.addWidget(QLabel(i18n.get("SCHEME")),1,0,1,1)
		cmbScheme=QComboBox()
		self.widgets.update({'scheme':cmbScheme})
		box.addWidget(cmbScheme,1,1,1,1)

		box.addWidget(QLabel(i18n.get("BACKGROUND")),2,0,1,1)
		cmbBackground=QComboBox()
		cmbBackground.setIconSize(QSize(self.bkgIconSize,self.bkgIconSize))
		self.widgets.update({'background':cmbBackground})
		box.addWidget(cmbBackground,2,1,1,1)

		box.addWidget(QLabel(i18n.get("SCALE")),3,0,1,1)
		cmbScale=QComboBox()
		self.widgets.update({'scale':cmbScale})
		box.addWidget(cmbScale,3,1,1,1)

		box.addWidget(QLabel(i18n.get("XSCALE")),4,0,1,1)
		cmbXscale=QComboBox()
		self.widgets.update({'xscale':cmbXscale})
		box.addWidget(cmbXscale,4,1,1,1)

		box.addWidget(QLabel(i18n.get("MAXIMIZE")),5,0,1,1)
		chkMax=QCheckBox()
		self.widgets.update({'chkmax':chkMax})
		box.addWidget(chkMax,5,1,1,1)

		box.addWidget(QLabel(i18n.get("CURSORTHEME")),6,0,1,1)
		cmbCursor=QComboBox()
		self.widgets.update({'cursor':cmbCursor})
		cmbCursor.currentIndexChanged.connect(self.updateCursorSizes)
		box.addWidget(cmbCursor,6,1,1,1)

		box.addWidget(QLabel(i18n.get("CURSORSIZE")),7,0,1,1)
		cmbCursorSize=QComboBox()
		self.widgets.update({'cursorSize':cmbCursorSize})
		box.addWidget(cmbCursorSize,7,1,1,1)
		cmbCursorSize.addItem("32")
		cmbCursorSize.addItem("48")
		cmbCursorSize.addItem("64")
		cmbCursorSize.addItem("80")
		cmbCursorSize.addItem("96")
		cmbCursorSize.addItem("112")
		cmbCursorSize.addItem("128")
		scr.setWidget(wdg)
		scr.setWidgetResizable(True)
	#def _load_screen

	def updateScreen(self):
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		self.changes=True
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
		selectedColor=""
		if config.get("bkg","")=="color":
			selectedColor=config.get("bkgColor","")
		theme=""
		self._fixBadThemePath()
		for value in self.plasmaConfig.get("kdeglobals",{}).get("General",[]):
			if value[0]=="Name":
				theme=value[1]
		for cmbDesc in self.widgets.keys():
			self._populateData(cmbDesc,config)

		if selectedColor!="":
			cmb=self.widgets.get("background",QComboBox())
			cmb.setCurrentText(i18n.get(selectedColor.upper(),selectedColor))
	#def _udpate_screen

	def _populateData(self,cmbDesc,config):
		cmb=self.widgets.get(cmbDesc,"")
		if isinstance(cmb,QComboBox):
			if cmbDesc=="cursorSize":
				self._loadCursorSize(cmb)
			elif cmbDesc=="scale" or cmbDesc=="xscale":
				self._loadScales(cmb,cmbDesc,config)
			else:
				if cmbDesc=="theme":
					themes=self._getThemeList()
				if cmbDesc=="scheme":
					themes=self._getSchemeList()
				if cmbDesc=="cursor":
					themes=self._getCursorList()
				if cmbDesc=="background":
					themes=self._fillBackgroundCmb()

				self._processThemeData(cmb,cmbDesc,themes)
				self._setCurrentItem(cmb,cmbDesc,config)
		elif isinstance(cmb,QCheckBox):
			if config.get("maximize","false")=="true":
				cmb.setChecked(True)
			else:
				cmb.setChecked(False)
	#def _populateData

	def _loadCursorSize(self,cmb):
		cmbT=self.widgets.get("cursor","")
		cmb.clear()
		theme=cmbT.currentText()
		theme=self.cursorDesc.get(theme,theme)
		img=self.accesshelper.getPointerImage(theme=theme)
		qsizes=img[1]
		sizes=[]
		for qsize in qsizes:
			if isinstance(qsize,QSize):
				if qsize.width() not in sizes:
					cmb.addItem(str(qsize.width()))
			else:
				if qsize not in sizes:
					if cmb.findText(qsize)==-1:
						cmb.addItem(qsize)
		cursorSize=32
		cursorSettings=self.plasmaConfig.get('kcminputrc',{}).get('Mouse',[])
		for setting in cursorSettings:
			if isinstance(setting,tuple):
				if setting[0]=="cursorSize":
					cursorSize=setting[1]
		cmb.setCurrentText(cursorSize)
	#def _loadCursorSize

	def _loadScales(self,cmb,cmbDesc,config):
		cmb.clear()
		cmb.addItem("100%")
		cmb.addItem("125%")
		cmb.addItem("150%")
		cmb.addItem("175%")
		cmb.addItem("200%")
		scale="100%"
		if cmbDesc=="scale":
			scaleFactor=self.accesshelper.getKdeConfigSetting("KScreen","ScaleFactor","kdeglobals")
			if isinstance(scaleFactor,str):
				if len(scaleFactor)>0:
					scale="{}%".format(str(int(float(scaleFactor)*100)))
			cmb.setCurrentText(scale)
		else:
			cmb.setCurrentText("{}%".format(config.get("xscale","100")))
	#def _loadScales

	def _processThemeData(self,cmb,cmbDesc,themes):
		for theme in themes:
			#themeDesc=theme.split("(")[0].replace("(","").rstrip(" ")
			themeDesc=theme.split("[")[0].strip()
			if cmb.findText(themeDesc)==-1:
				if cmbDesc=="cursor":
					#i18n could translate the description, real name needed
					cursorTheme=theme.split("[")[1].split(" ")[0].replace("]","")
					icon,sizes=self._getPointerImage(cursorTheme)
					if icon:
						cmb.addItem(icon,themeDesc)
					else:
						cmb.addItem(themeDesc)
					self.cursorDesc[themeDesc]=cursorTheme
				elif cmbDesc=="background":
					color=theme.split("[")[1].replace("[","").replace("]","")
					px=QtGui.QPixmap(self.bkgIconSize,self.bkgIconSize)
					if os.path.isfile(color):
						px.load(color)
					elif color:
						px.fill(QtGui.QColor(color))
					icon=QtGui.QIcon(px)
					cmb.addItem(icon,themeDesc.strip())
				elif cmbDesc!="cursorSize":
					arrayThemeDesc=themeDesc.split("(")
					cmb.addItem(arrayThemeDesc[0].strip())
	#def _processThemeData

	def _setCurrentItem(self,cmb,cmbDesc,config):
		searchedTheme=config.get("theme","")
		if searchedTheme=="":
			searchedTheme=self.accesshelper.getCurrentTheme()
		if cmbDesc=="theme" and searchedTheme!="":
			cmb.setCurrentText(config.get("theme"))
		elif cmbDesc=="cursor" and config.get("cursor","")!="":
			searchedTheme=config.get("cursor")
			if "[" in searchedTheme:
				searchedTheme=searchedTheme.split("[")[0].strip()
			sw=False
			for key,item in self.cursorDesc.items():
				if searchedTheme==item:
					sw=True
					cmb.setCurrentText(key)
					break
			if sw==False:
				searchedTheme=self.accesshelper.getCursorTheme()
				for key,item in self.cursorDesc.items():
					if searchedTheme==item:
						sw=True
						cmb.setCurrentText(key)
						break
		elif cmbDesc=="scheme" and config.get("scheme","")!="":
			cmb.setCurrentText(config.get("scheme"))
	#def _setCurrentItem

	def _fixBadThemePath(self):
		#Check if lookandfeel has been configured before
		home=os.environ.get('HOME')
		thematizer=os.path.join(home,".config/autostart/accesshelper_thematizer.desktop")
		content=[]
		fixExec=False
		if os.path.isfile(thematizer):
			with open(thematizer,'r') as f:
				content=f.readlines()
			#Fix bad path in thematizer autostart. Delete it.
			for line in content:
				if line.startswith("Exec="):
					if line.startswith("Exec=/usr/share/accesshelper/thematizer.sh"):
						os.remove(thematizer)
					break
	#def _fixBadThemePath(self):

	def updateCursorIcons(self):
		cmbSize=self.widgets.get("cursorSize")
		cmbCursors=self.widgets.get("cursor")
		if cmbSize.currentText()=='' or cmbSize.currentText().isdigit()==False:
			cmbSize.setCurrentText("32")
		cmbCursors.setIconSize(QSize(int(cmbSize.currentText()), int(cmbSize.currentText())))
		cmbCursors.adjustSize()
	#def updateSizes

	def updateCursorSizes(self):
		cmb=self.widgets.get("cursorSize")
		self._loadCursorSize(cmb)
	#def updateCursorSizes(self):

	def _fillBackgroundCmb(self):
		if self.imgFile=="":
			imgFile=self.accesshelper.getBackgroundImg()
			if imgFile=="":
				imgFile="white"
			else:
				self.imgFile=imgFile
		else:
			imgFile=self.imgFile
		colors=["{0} [{1}]".format(i18n.get("CURRENTBKG","Current background"),imgFile)]
		colorList=["black","red","blue","green","yellow","white"]
		for color in colorList:
			desc=i18n.get(color.upper(),color)
			colors.append("{0} [{1}]".format(desc,color))
		return(colors)
	#def _fillBackgroundCmb
		
	def _getPointerImage(self,theme):
		return(self.accesshelper.getPointerImage(theme=theme))
	#def _getPointerImage(self,theme):

	def _getThemeList(self):
		availableThemes=self.accesshelper.getThemes()
		return (availableThemes)
	#def _getThemeList

	def _getSchemeList(self):
		availableSchemes=self.accesshelper.getSchemes()
		return (availableSchemes)
	#def _getSchemeList

	def _getCursorList(self):
		availableThemes=self.accesshelper.getCursors()
		return (availableThemes)
	#def _getCursorList

	def _getScales(self):
		return(["100%","125%","150%","175%","200%"])
	#def _getScales

	def _setTheme(self,theme):
		self._debug("Setting theme to {}".format(theme))
		self.accesshelper.setThemeSchemeLauncher(theme=theme)
	#def _setTheme

	def _setScheme(self,scheme):
		self._debug("Setting scheme to {}".format(scheme))
		self.accesshelper.setThemeSchemeLauncher(scheme=scheme)
	#def _setScheme

	def _setCursor(self,themeDesc,size):
		theme=self.cursorDesc.get(themeDesc,themeDesc)
		self._debug("Set cursor theme: {} was {}".format(theme,themeDesc))
		self.accesshelper.setCursor(theme,size)
	#def _setCursor

	def _setCursorSize(self,size):
		self.saveChanges('cursor',{"size":size})
		self.accesshelper.setCursorSize(size)
	#def _setCursorSize(self):

	def writeConfig(self):
		self.optionChanged=[]
		self.refresh=True
		cursorTheme=""
		size=""
		scheme=""
		plasmaTheme=""
		maximize="false"
		if self.widgets.get("chkmax").checkState()==Qt.CheckState.Checked:
			maximize="true"
		for cmbDesc in self.widgets.keys():
			cmb=self.widgets.get(cmbDesc,"")
			if isinstance(cmb,QComboBox):
				theme=cmb.currentText()
				theme=theme.split("(")[0].strip()
				if cmbDesc=="theme":
					plasmaTheme=theme
				if cmbDesc=="scheme":
					scheme=theme
				if cmbDesc=="cursor":
					cursorTheme=theme
				if cmbDesc=="cursorSize":
					size=cmb.currentText()
				if cmbDesc=="scale":
					scale=cmb.currentText().replace("%","")
					scaleFactor=round(float(scale)/100,2)
					self.accesshelper.setScaleFactor(scaleFactor,xrand=False)
				if cmbDesc=="xscale":
					xscale=cmb.currentText().replace("%","")
					if xscale=="100":
						self.accesshelper.removeXscale()
					else:
						self.accesshelper.setXscale(xscale,autostart=True)
				if cmbDesc=="background":
					idx=cmb.currentIndex()
					if idx>0:
						qcolor=""
						color=cmb.currentText().strip()
						colorList=["black","red","blue","green","yellow","white"]
						for i18color in colorList:
							if i18n.get(i18color.upper(),"")==color:
								qcolor=QtGui.QColor(i18color)
								break
						bkg=color
						self.saveChanges('bkgColor',i18color)
						self.saveChanges('bkg',"color")
					elif self.imgFile:
						self.saveChanges('bkg',"image")
						self.saveChanges('bkg',self.imgFile)
		self.saveChanges('theme',plasmaTheme)
		self.saveChanges('maximize',maximize)
		self.saveChanges('scheme',scheme)
		self.saveChanges('cursor',self.cursorDesc.get(cursorTheme,cursorTheme))
		self.saveChanges('cursorSize',size)
		self.saveChanges('scale',scale)
		self.saveChanges('xscale',xscale)
		self._writeFileChanges(scheme,plasmaTheme,cursorTheme,size,bkg,scale,xscale,maximize)
	#def writeConfig

	def _writeFileChanges(self,scheme,theme,cursor,cursorSize,bkg,scale,xscale,maximize):
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			f.write("{0}->{1}\n".format(i18n.get("THEME"),theme))
			f.write("{0}->{1}\n".format(i18n.get("SCHEME"),scheme))
			f.write("{0}->{1}\n".format(i18n.get("CURSORTHEME"),self.cursorThemes.get(cursor,cursor)))
			f.write("{0}->{1}\n".format(i18n.get("CURSORSIZE"),cursorSize))
			f.write("{0}->{1}\n".format(i18n.get("BACKIMG"),bkg))
			f.write("{0}->{1}\n".format(i18n.get("SCALE"),scale))
			f.write("{0}->{1}\n".format(i18n.get("XSCALE"),xscale))
			f.write("{0}->{1}\n".format(i18n.get("MAXIMIZE"),i18n.get(str(maximize).upper())))

	#def _writeFileChanges(self):

