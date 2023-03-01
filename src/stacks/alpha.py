#!/usr/bin/python3
from . import libaccesshelper
import sys
import os
import subprocess
from PySide2.QtWidgets import QWidget, QPushButton,QGridLayout,QCheckBox,QScrollArea,QColorDialog,QGroupBox,QListView,QFrame
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
	"DESCRIPTION":_("Color filter"),
	"MENUDESCRIPTION":_("Modify screen color levels"),
	"TOOLTIP":_("Set color filter for the screen"),
	"FILTER":_("Color filter"),
	"DEFAULT":_("By default"),
	"OPTIONCOLOR":_("Set color filter: ")
	}

class _QColorWidget(QColorDialog):
	def __init__(self,color=None,parent=None):
		QColorDialog.__init__(self, parent)
		if color:
			self.setColor(color)
		self.installEventFilter(self)

	def eventFilter(self, source,event):
		#Block all
		return True
#class _QColorDialog

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
		self.embebbed=False
		self.scr=None
		self.widgets={}
		self.accesshelper=libaccesshelper.accesshelper()
	#def __init__

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		kdevalues=self.plasmaConfig.get('kgammarc',{}).get('Screen 0',[])
		(dlgColor,wdg)=self._QcolorWidget()	
		scr=QScrollArea()
		scr.setWidget(dlgColor)
		scr.setWidgetResizable(True)
		scr.setStyleSheet("""QScrollArea{background-color:rgba(155,155,155,0)}""")
		self.box.addWidget(scr)
		self.widgets.update({"alpha":wdg})
		self.btn_cancel.setText(i18n.get("DEFAULT"))
		self.btn_cancel.setEnabled(True)
		#self.btn_ok.released.connect(self.updateScreen)
	#def _load_screen

	def _QcolorWidget(self):
		wdg=QWidget()
		lay=QGridLayout()
		cwdg=_QColorWidget()
		lay.addWidget(cwdg)
		wdg.setLayout(lay)
		#Embed in window
		cwdg.setWindowFlags(Qt.Widget)
		cwdg.setOptions(cwdg.NoButtons)
		#Customize widget
		for chld in wdg.findChildren(QGroupBox):
			for groupChld in chld.findChildren(QCheckBox):
				chld.hide()
				break
		return(wdg,cwdg)

	def _enableDefault(self,*args):
		self.btn_cancel.setEnabled(True)
	#def _enableDefault

	def setCurrentColor(self,rgba):
		if isinstance(rgba,QtGui.QColor):
			wdg=self.widgets.get('alpha')
			if wdg:
				wdg.setCurrentColor(rgba)
	#def setCurrentColor

	def updateScreen(self):
		self.refresh=True
		try:
			self.config=self.getConfig()
		except:
			self.config={}
		finally:
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
		if self.config==None:
			self.config=self.getConfig()
		qalpha=self.widgets.get("alpha").currentColor()
		if (qalpha.red()+qalpha.blue()+qalpha.green()+qalpha.alpha())==255*4:
			self.accesshelper.removeRGBFilter()
			(red,green,blue)=(1.0,1.0,1.0)
			qalpha=None
		else:
			(red,green,blue)=self.accesshelper.setRGBFilter(qalpha,self.embebbed)
		if self.embebbed==False:
			if isinstance(qalpha,QtGui.QColor):
				self.saveChanges("alpha",qalpha.getRgb())
				self._writeFileChanges(qalpha.getRgb())
			else:
				self.saveChanges("alpha",[])
				self._writeFileChanges([i18n.get("DEFAULT")])
			self.optionChanged=[]
			self.refresh=True
			self.btn_cancel.setEnabled(True)
	#def writeConfig

	def _reset_screen(self,*args):
		self.accesshelper.removeRGBFilter()
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
		self.optionChanged=[]
		if self.appConfig:
			self.saveChanges('alpha',[])
		dlgColor=self.widgets.get('alpha')
		dlgColor.setCurrentColor("white")
		self.changes=False
		self.refresh=False
	#def _reset_screen

	def _writeFileChanges(self,filter):
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			f.write("{0}->{1}\n".format(i18n.get("FILTER"),filter))
	#def _writeFileChanges(self):
