#!/usr/bin/python3
from . import libaccesshelper
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
	"CONFIG":_("Fonts"),
	"DESCRIPTION":_("Fonts"),
	"MENUDESCRIPTION":_("Modify system fonts"),
	"TOOLTIP":_("Customize the system fonts"),
	"FONTSIZE":_("Font size"),
	"FAMILY":_("Font family"),
	"CURSORTHEME":_("Cursor theme"),
	"CURSORSIZE":_("Cursor size"),
	"SETFONT":_("Font")
	}
class _QFontDialog(QFontDialog):
	def __init__(self,font=None,parent=None):
		QFontDialog.__init__(self, parent)
		if font:
			self.setFont(font)
		else:
			print(self.font())
			self.setFont(self.font())
		self.installEventFilter(self)

	def eventFilter(self, source,event):
		#Block all
		return True
#class _QFontDialog

class fonts(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("fonts load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-font')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=5
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
		self.config={}
		self.plasmaConfig={}
		self.wrkFiles=["kdeglobals","kcminputrc","konsolerc"]
		self.blockSettings={}
		self.wantSettings={"kdeglobals":["General"]}
		self.optionChanged=[]
		self.accesshelper=libaccesshelper.accesshelper()
		self.btn_cancel.setVisible(False)
	#def __init__

	def _readKdeConfig(self):
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
	 #def _readKdeConfig

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self._readKdeConfig()
		kdevalues=self.plasmaConfig.get('kdeglobals',{}).get('General',[])
		font=''
		for value in kdevalues:
			if isinstance(value,tuple):
				if value[0]=='font':
					font=value[1]
					break
		dlgFont=_QFontDialog(font)
		#Embed in window
		dlgFont.setWindowFlags(Qt.Widget)
		dlgFont.setOptions(dlgFont.NoButtons)
		#Customize widget
		for chld in dlgFont.findChildren(QGroupBox):
			for groupChld in chld.findChildren(QCheckBox):
				chld.hide()
				break

		row,col=(0,0)
		self.box.addWidget(dlgFont)
		self.widgets={}
		self.widgets.update({"font":dlgFont})
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
	#def _load_screen

	def _noClose(self,*args,**kwargs):
		print("PPPP")
		print(args,kwargs)
		args=()
		return(False)
	#def _noClos

	def updateScreen(self):
		self.config=self.getConfig()
		self._readKdeConfig()
		kdevalues=self.plasmaConfig.get('kdeglobals',{}).get('General',[])
		for value in kdevalues:
			if isinstance(value,tuple):
				if value[0]=='font':
					font=value[1]
					break
		if font=="":
			font=self.font().toString()
		qfont=QtGui.QFont(font)
		dlgFont=self.widgets.get('font')
		dlgFont.setCurrentFont(font)
		#fix listview selections
		try:
			family=font.split(",")[0]
			style=font.split(",")[-1]
			size=font.split(",")[1]
		except:
			style="Regular"
			size="12"
			family="Noto Sans"
		for chld in dlgFont.findChildren(QListView):
			sw_alpha=True
			model=chld.model()
			if style:
				if style.isdigit():
					style="Regular"
				for row in range(model.rowCount()):
					index=model.index(row,0)
					data=model.data(index)
					if data==family:
						chld.setCurrentIndex(index)
						break
					if data==style:
						chld.setCurrentIndex(index)
						break
					if data==size:
						chld.setCurrentIndex(index)
			chld.scrollTo(chld.currentIndex(),chld.PositionAtTop)
		for chld in dlgFont.findChildren(QComboBox):
			chld.setCurrentIndex(1)
		config=self.config.get(self.level,{})
	#def _udpate_screen

	def writeConfig(self):
		wdg=self.widgets.get("font")
		qfont=wdg.currentFont()
		font=qfont.toString()
		minfont=font
		size=qfont.pointSize()
		minSize=size-2
		self._debug("FONT: {}".format(size))
		self.saveChanges('font','{}'.format(font))
		self.saveChanges('fontSize','{}'.format(size))
		self.saveChanges('mozillaFontSize','{}'.format(size+7))
		fontFixed="Hack"
		fixed="{0},{1},-1,5,50,0,0,0,0,0".format(fontFixed,size)
		if size>8:
			qfont.setPointSize(size-2)
			minFont=qfont.toString()
		self.accesshelper.setKdeConfigSetting("General","fixed",fixed,"kdeglobals")
		self.accesshelper.setKdeConfigSetting("General","font",font,"kdeglobals")
		self.accesshelper.setKdeConfigSetting("General","menuFont",font,"kdeglobals")
		self.accesshelper.setKdeConfigSetting("General","smallestReadableFont",minFont,"kdeglobals")
		self.accesshelper.setKdeConfigSetting("General","toolBarFont",font,"kdeglobals")
		self.accesshelper.setKdeConfigSetting("WM","activeFont",font,"kdeglobals")
		self.accesshelper.setKdeConfigSetting("Appearance","Font",fixed,"Lliurex.profile")
		self.accesshelper.setMozillaFirefoxFonts(size+7)
		self.accesshelper.setGtkFonts(font)
		self._writeFileChanges(font)
	#def writeConfig

	def _writeFileChanges(self,font):
		arrayFont=font.split(",")
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			f.write("{0}->{1} {2} {3}\n".format(i18n.get("SETFONT"),arrayFont[0],arrayFont[1],arrayFont[-1]))
	#def _writeFileChanges(self):
