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
	"DESCRIPTION":_("Font configuration"),
	"MENUDESCRIPTION":_("Modify system fonts"),
	"TOOLTIP":_("Customize the system fonts"),
	"FONTSIZE":_("Font size"),
	"FAMILY":_("Font family"),
	"CURSORTHEME":_("Cursor theme"),
	"CURSORSIZE":_("Cursor size"),
	"SETFONT":_("Font")
	}

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

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		kdevalues=self.plasmaConfig.get('kdeglobals',{}).get('General',[])
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
		kdevalues=self.plasmaConfig.get('kdeglobals',{}).get('General',[])
		for value in kdevalues:
			if isinstance(value,tuple):
				if value[0]=='font':
					font=value[1]
					break
		qfont=QtGui.QFont(font)
		dlgFont=self.widgets.get('font')
		dlgFont.setCurrentFont(font)
		#fix listview selections
		try:
			style=font.split(",")[-1]
			size=font.split(",")[1]
		except:
			style=""
			size=""
		for chld in dlgFont.findChildren(QListView):
			sw_alpha=True
			model=chld.model()
			if style:
				if style.isdigit():
					style="Regular"
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
		for chld in dlgFont.findChildren(QListView):
			model=chld.model()
			if size.isdigit():
				sw_num=True
				for row in range(model.rowCount()):
					index=model.index(row,0)
					data=model.data(index)
					if data==size:
						chld.setCurrentIndex(index)
						break
					elif data.isdigit==False:
						sw_num=False
						break
				if sw_num==False:
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
