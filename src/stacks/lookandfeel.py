#!/usr/bin/python3
from . import libaccesshelper
import sys
import os,shutil
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
	"WHITE":_("White"),
	"RED":_("Red"),
	"BLUE":_("Blue"),
	"GREEN":_("Green"),
	"YELLOW":_("Yellow"),
	"BLACK":_("Black"),
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
		self.defaultRepos={}
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
		self.accesshelper=libaccesshelper.accesshelper()
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
		if config.get("background"):
			self.imgFile=config.get("background")

		self.box.addWidget(QLabel(i18n.get("THEME")),0,0,1,1)
		cmbTheme=QComboBox()
		self.widgets.update({'theme':cmbTheme})
		self.box.addWidget(cmbTheme,0,1,1,1)

		self.box.addWidget(QLabel(i18n.get("SCHEME")),1,0,1,1)
		cmbScheme=QComboBox()
		self.widgets.update({'scheme':cmbScheme})
		self.box.addWidget(cmbScheme,1,1,1,1)

		self.box.addWidget(QLabel(i18n.get("BACKGROUND")),2,0,1,1)
		cmbBackground=QComboBox()
		cmbBackground.setIconSize(QSize(self.bkgIconSize,self.bkgIconSize))
		self.widgets.update({'background':cmbBackground})
		self.box.addWidget(cmbBackground,2,1,1,1)

		self.box.addWidget(QLabel(i18n.get("SCALE")),3,0,1,1)
		cmbScale=QComboBox()
		self.widgets.update({'scale':cmbScale})
		self.box.addWidget(cmbScale,3,1,1,1)

		self.box.addWidget(QLabel(i18n.get("XSCALE")),4,0,1,1)
		cmbXscale=QComboBox()
		self.widgets.update({'xscale':cmbXscale})
		self.box.addWidget(cmbXscale,4,1,1,1)

		self.box.addWidget(QLabel(i18n.get("CURSORTHEME")),5,0,1,1)
		cmbCursor=QComboBox()
		self.widgets.update({'cursor':cmbCursor})
		cmbCursor.currentIndexChanged.connect(self.updateCursorSizes)
		self.box.addWidget(cmbCursor,5,1,1,1)

		self.box.addWidget(QLabel(i18n.get("CURSORSIZE")),6,0,1,1)
		cmbCursorSize=QComboBox()
		self.widgets.update({'cursorSize':cmbCursorSize})
		self.box.addWidget(cmbCursorSize,6,1,1,1)
		cmbCursorSize.addItem("32")
		cmbCursorSize.addItem("48")
		cmbCursorSize.addItem("64")
		cmbCursorSize.addItem("80")
		cmbCursorSize.addItem("96")
		cmbCursorSize.addItem("112")
		cmbCursorSize.addItem("128")
	#def _load_screen

	def updateScreen(self):
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
		selectedColor=""
		if config.get("bkg","")=="color":
			selectedColor=config.get("bkgColor","")
		theme=""
		#Check if lookandfeel has been configured before
		home=os.environ.get('HOME')
		thematizer=os.path.join(home,".config/autostart/accesshelper_thematizer.desktop")
		nextTheme=""
		nextScheme=""
		content=[]
		fixExec=False
		if os.path.isfile(thematizer):
			with open(thematizer,'r') as f:
				content=f.readlines()
			for line in content:
				if line.startswith("Exec="):
					if line.startswith("Exec=/usr/share/accesshelper/thematizer.sh"):
						fixExec=True
					array=line.split(" ")
					if len(array)>1:
						nextTheme=array[1].replace("\n","")
					if len(array)>2:
						nextScheme=array[2].replace("\n","")
					break
		#Fix bad path in thematizer autostart. Delete it.
		if fixExec and len(content)>0:
			if os.path.isfile(thematizer):
				os.remove(thematizer)
				nextScheme=""
		for value in self.plasmaConfig.get("kdeglobals",{}).get("General",[]):
			if value[0]=="Name":
				theme=value[1]
		for cmbDesc in self.widgets.keys():
			cmb=self.widgets.get(cmbDesc,"")
			if isinstance(cmb,QComboBox):
				if cmbDesc=="cursorSize":
					cursorSize=32
					cursorSettings=self.plasmaConfig.get('kcminputrc',{}).get('Mouse',[])
					for setting in cursorSettings:
						if isinstance(setting,tuple):
							if setting[0]=="cursorSize":
								cursorSize=setting[1]
					if cmb.findText(cursorSize)==-1 and isinstance(cursorSize,int):
						cmb.insertItem(0,cursorSize)
					cmb.setCurrentText(cursorSize)
				elif cmbDesc=="scale" or cmbDesc=="xscale":
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
				else:
					if cmbDesc=="theme":
						themes=self._getThemeList()
					if cmbDesc=="scheme":
						themes=self._getSchemeList()
					if cmbDesc=="cursor":
						themes=self._getCursorList()
					if cmbDesc=="background":
						themes=self._fillBackgroundCmb()

					for theme in themes:
						#themeDesc=theme.split("(")[0].replace("(","").rstrip(" ")
						themeDesc=theme.split("[")[0]
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
								cmb.addItem(icon,themeDesc)
							elif cmbDesc!="cursorSize":
								cmb.addItem(themeDesc)

						if cmbDesc=="theme" and nextTheme!="":
							cmb.setCurrentText(nextTheme)
						elif cmbDesc=="scheme" and nextScheme!="":
							cmb.setCurrentText(nextScheme)
						elif "(" in theme:
							cmb.setCurrentText(themeDesc)
			if selectedColor!="":
				cmb=self.widgets.get("background",QComboBox())
				cmb.setCurrentText(i18n.get(selectedColor.upper(),selectedColor))
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

	def _fillBackgroundCmb(self):
		if self.imgFile=="":
			imgFile=self.accesshelper.getBackgroundImg()
			self.imgFile=imgFile
		else:
			imgFile=self.imgFile
		if imgFile=="":
			imgFile="white"
		colors=["{0} [{1}]".format(i18n.get("CURRENTBKG","Current background"),imgFile)]
		colorList=["black","red","blue","green","yellow","white"]
		for color in colorList:
			desc=i18n.get(color.upper(),color)
			colors.append("{0} [{1}]".format(desc,color))
		return(colors)
		
	def _getPointerImage(self,theme):
		return(self.accesshelper.getPointerImage(theme=theme))

	def _updateConfig(self,key):
		return
		#	if key in self.kwinMethods:
		#		self._exeKwinMethod(key) 
	
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

	def _setTheme(self,theme):
		#self.accesshelper.setTheme(theme)
		self._setThemeSchemeLauncher(theme=theme)
	#def _setTheme

	def _setScheme(self,scheme):
		print("Setting scheme to {}".format(scheme))
#		with open("/tmp/.set_scheme","w") as f:
#			f.write(scheme)
		self._setThemeSchemeLauncher(scheme=scheme)
		#Apply scheme change on exit

	#def _setScheme

	def _setThemeSchemeLauncher(self,theme="",scheme=""):
		home=os.environ.get('HOME')
		if home:
			autostart=os.path.join(home,".config/autostart")
			if os.path.isdir(autostart)==False:
				os.makedirs(autostart)
			desktop="accesshelper_thematizer.desktop"
			source=os.path.join("/usr/share/accesshelper/helper/",desktop)
			destpath=os.path.join(autostart,desktop)
			content=[]
			newcontent=[]
			if os.path.isfile(destpath):
				with open(destpath,'r') as f:
					content=f.readlines()
			elif os.path.isfile(source):
				with open(source,'r') as f:
					content=f.readlines()
			for line in content:
				newline=line
				if line.startswith("Exec="):
					array=line.split(" ")
					if theme:
						array[1]=theme
					if scheme:
						array[2]=scheme
					newline=" ".join(array)
				newcontent.append(newline)
			with open(destpath,'w') as f:
				f.writelines(newcontent)
				f.write("\n")
	#def _setThemeSchemeLauncher

	def _setCursor(self,themeDesc,size):
		theme=self.cursorDesc.get(themeDesc,themeDesc)
		self._debug("Set cursor theme: {} was {}".format(theme,themeDesc))
		self.accesshelper.setCursor(theme,size)
	#def _setCursor

	def _setCursorSize(self,size):
		self.saveChanges('cursor',{"size":size})
		self.accesshelper.setCursorSize(size)
	#def _setCursorSize(self):

	def _setScale(self,scaleFactor):
		self.accesshelper.setScaleFactor(scaleFactor,xrand=False)

	def writeConfig(self):
		self.saveChanges('background',self.imgFile)
		self.optionChanged=[]
		self.refresh=True
		cursorTheme=""
		size=""
		scheme=""
		plasmaTheme=""
		for cmbDesc in self.widgets.keys():
			cmb=self.widgets.get(cmbDesc,"")
			if isinstance(cmb,QComboBox):
				theme=cmb.currentText()
				theme=theme.split("(")[0].strip()
				if cmbDesc=="theme":
					plasmaTheme=theme
					self._setTheme(theme)
				if cmbDesc=="scheme":
					scheme=theme
					self._setScheme(theme)
				if cmbDesc=="cursor":
					cursorTheme=theme
				if cmbDesc=="cursorSize":
					size=cmb.currentText()
				if cmbDesc=="scale":
					scale=cmb.currentText().replace("%","")
					scaleFactor=round(float(scale)/100,2)
					self._setScale(scaleFactor)
				if cmbDesc=="xscale":
					xscale=cmb.currentText().replace("%","")
					if xscale=="100":
						self.accesshelper.removeXscale()
					else:
						self.accesshelper.setXscale(xscale)
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
						self.saveChanges('bkgColor',i18color)
						self.saveChanges('bkg',"color")
						if qcolor:
							self.accesshelper.setBackgroundColor(qcolor)
						bkg=color
					else:
						self.saveChanges('bkg',"image")
						self.accesshelper.setBackgroundImg(self.imgFile)
						bkg=self.imgFile
		#Ensure size is applied before theme change
		#self._setCursorSize(size)
		self.saveChanges('cursor',cursorTheme)
		self.saveChanges('cursorSize',size)
		self.saveChanges('scale',scale)
		self.saveChanges('xscale',xscale)
		self._setCursor(cursorTheme,size)
		self._writeFileChanges(scheme,plasmaTheme,cursorTheme,size,bkg,scale)
	#def writeConfig

	def _writeFileChanges(self,scheme,theme,cursor,cursorSize,bkg,scale):
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			f.write("{0}->{1}\n".format(i18n.get("THEME"),theme))
			f.write("{0}->{1}\n".format(i18n.get("SCHEME"),scheme))
			f.write("{0}->{1}\n".format(i18n.get("CURSORTHEME"),cursor))
			f.write("{0}->{1}\n".format(i18n.get("CURSORSIZE"),cursorSize))
			f.write("{0}->{1}\n".format(i18n.get("BACKIMG"),bkg))
			f.write("{0}->{1}\n".format(i18n.get("SCALE"),scale))
			f.write("{0}->{1}\n".format(i18n.get("XSCALE"),xscale))
	#def _writeFileChanges(self):

