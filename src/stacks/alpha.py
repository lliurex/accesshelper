#!/usr/bin/python3
from . import libaccesshelper
import sys
import os
import subprocess
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTabBar,QTabWidget,QTabBar,QTabWidget,QSlider,QToolTip,QListWidget,QColorDialog,QGroupBox,QListView,QFrame
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper,QEvent
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import json
import dbus,dbus.service,dbus.exceptions
QString=type("")

i18n={
	"CONFIG":_("Color"),
	"DESCRIPTION":_("Color filter configuration"),
	"MENUDESCRIPTION":_("Modify screen color levels"),
	"TOOLTIP":_("Set color filter for the screen"),
	"FILTER":_("Color filter"),
	"DEFAULT":_("By default"),
	"OPTIONCOLOR":_("Set color filter: ")
	}

class alpha(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("alpha load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-color')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=3
		self.enabled=True
		self.changed=[]
		self.config={}
		self.plasmaConfig={}
		self.wrkFiles=["kgammarc"]
		self.blockSettings={}
		self.optionChanged=[]
		self.accesshelper=libaccesshelper.accesshelper()
	#def __init__

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		kdevalues=self.plasmaConfig.get('kgammarc',{}).get('Screen 0',[])
		dlgColor=QColorDialog()
		#Embed in window
		dlgColor.setWindowFlags(Qt.Widget)
		dlgColor.setOptions(dlgColor.NoButtons)
		#Customize widget
		for chld in dlgColor.findChildren(QGroupBox):
			for groupChld in chld.findChildren(QCheckBox):
				chld.hide()
				break
		cont=0
		row,col=(0,0)
		self.box.addWidget(dlgColor)
		self.widgets={}
		self.widgets.update({"alpha":dlgColor})
		self.btn_cancel.setText(i18n.get("DEFAULT"))
		self.btn_cancel.setEnabled(True)
		#self.btn_ok.released.connect(self.updateScreen)
	#def _load_screen

	def _enableDefault(self,*args):
		self.btn_cancel.setEnabled(True)
	#def _enableDefault

	def updateScreen(self):
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
		alpha=config.get('alpha',[])
		dlgColor=self.widgets.get('alpha')
		if len(alpha)==4:
			dlgColor.setCurrentColor(QtGui.QColor(alpha[0],alpha[1],alpha[2],alpha[3]))
		config=self.config.get(self.level,{})
		alpha=config.get('alpha',[])
		self.btn_cancel.setEnabled(True)
		self.btn_cancel.adjustSize()
	#def _udpate_screen

	def _updateConfig(self,key):
		return
	#def _updateConfig
	
	def writeConfig(self):
		qalpha=self.widgets.get("alpha").currentColor()
		(red,green,blue)=self.accesshelper.setRGBFilter(qalpha)
		self.plasmaConfig['kgammarc']['ConfigFile']=[("use","kgammarc")]
		self.plasmaConfig['kgammarc']['SyncBox']=[("sync","yes")]
		values=[]
		for gamma in self.plasmaConfig['kgammarc']['Screen 0']:
			(desc,value)=gamma
			if desc=='bgamma':
				values.append((desc,"{0:.2f}".format(blue)))
			elif desc=='rgamma':
				values.append((desc,"{0:.2f}".format(red)))
			elif desc=='ggamma':
				values.append((desc,"{0:.2f}".format(green)))
		self.plasmaConfig['kgammarc']['Screen 0']=values
		self.accesshelper.setPlasmaConfig(self.plasmaConfig)
		self.saveChanges("alpha",qalpha.getRgb())
		self.optionChanged=[]
		self.refresh=True
		self.btn_cancel.setEnabled(True)
		self._writeFileChanges(qalpha)
	#def writeConfig

	def _reset_screen(self,*args):
		self.accesshelper.removeRGBFilter()
		self.btn_ok.setEnabled(False)
		self.btn_cancel.setEnabled(True)
		self.optionChanged=[]
		self.saveChanges('alpha',[])
		dlgColor=self.widgets.get('alpha')
		dlgColor.setCurrentColor("white")
		self.changes=False
		self.refresh=False
	#def _reset_screen

	def _writeFileChanges(self,qalpha):
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}<b>\n".format(i18n.get("CONFIG")))
			f.write("{0}->{1}\n".format(i18n.get("FILTER"),qalpha.getRgb()))
	#def _writeFileChanges(self):
