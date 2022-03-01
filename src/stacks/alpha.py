#!/usr/bin/python3
from . import functionHelper
from . import resolutionHelper
import sys
import os
import subprocess
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QTabBar,QTabWidget,QTabBar,QTabWidget,QSlider,QToolTip,QListWidget,QColorDialog,QGroupBox,QListView
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper,QEvent
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import json
import dbus,dbus.service,dbus.exceptions
QString=type("")

i18n={
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Color filter configuration"),
	"MENUDESCRIPTION":_("Modify screen color levels"),
	"TOOLTIP":_("Set color filter for the screen"),
	"FILTER":_("Color filter"),
	}

class alpha(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("alpha load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-color')
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
		self.box=QGridLayout()
		self.setLayout(self.box)
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile=wrkFile)
			self.sysConfig.update(systemConfig)
		kdevalues=self.sysConfig.get('kdeglobals',{}).get('General',[])
		alpha=''
		for value in kdevalues:
			if isinstance(value,tuple):
				if value[0]=='alpha':
					alpha=value[1]
					break
		dlgColor=QColorDialog()
		#Embed in window
		dlgColor.setWindowFlags(Qt.Widget)
		dlgColor.setOptions(dlgColor.NoButtons)
		#dlgColor.currentColorChanged.connect(self._dlgChange)
		#Customize widget
		for chld in dlgColor.findChildren(QGroupBox):
			for groupChld in chld.findChildren(QCheckBox):
				chld.hide()
				break

		row,col=(0,0)
		self.box.addWidget(dlgColor)
		#sigmap_run=QSignalMapper(self)
		#sigmap_run.mapped[QString].connect(self._updateConfig)
		self.widgets={}
		self.widgets.update({"alpha":dlgColor})
		self.config=self.getConfig()
		config=self.config.get(self.level,{})
		self.btn_ok.released.connect(self.updateScreen)
		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		self.config=self.getConfig()
		qalpha=QtGui.QColor()
		dlgColor=self.widgets.get('alpha')
		config=self.config.get(self.level,{})
		self.btn_cancel.setEnabled(True)
	#def _udpate_screen

	def _updateConfig(self,key):
		return
		#	if key in self.kwinMethods:
		#		self._exeKwinMethod(key) 
	
	def writeConfig(self):
		for name,wdg in self.widgets.items():
			if name=="alpha":
				alpha=wdg.currentColor()
				red=alpha.red()/100
				blue=alpha.blue()/100
				green=alpha.green()/100
				brightness=1
				for monitor in self._getMonitors():
					self._debug("Selected monitor {}".format(monitor))
					self._debug("R: {0} G: {1} B: {2}".format(red,green,blue))
					xrand=["xrandr","--output",monitor,"--gamma","{0}:{1}:{2}".format(red,green,blue),"--brightness",str(brightness)]
					cmd=subprocess.run(xrand,capture_output=True,encoding="utf8")
					self._debug(" ".join(["xrandr","--output",monitor,"--gamma","{0}:{1}:{2}".format(red,green,blue),"--brightness",str(brightness)]))
					self._generateAutostartDesktop(xrand)
				self.saveChanges('alpha','{}:{}:{}'.format(alpha.red(),alpha.green(),alpha.blue()))
		self.optionChanged=[]
		self.refresh=True
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
	#def writeConfig

	def _reset_screen(self,*args):
		for monitor in self._getMonitors():
			xrand=["xrandr","--output",monitor,"--gamma","1:1:1","--brightness","1"]
			cmd=subprocess.run(xrand,capture_output=True,encoding="utf8")
		self.btn_ok.setEnabled(False)
		self.saveChanges('alpha','1:1:1')
		self._removeAutostartDesktop()
	#def _reset_screen

	def _getMonitors(self):
		monitors=[]
		cmd=subprocess.run(["xrandr","--listmonitors"],capture_output=True,encoding="utf8")
		for xrandmonitor in cmd.stdout.split("\n"):
			monitor=xrandmonitor.split(" ")[-1].strip()
			if not monitor or monitor.isdigit()==True:
				continue
			monitors.append(monitor)
		return(monitors)
	#def _getMonitors

	def _generateAutostartDesktop(self,cmd):
		desktop=[]
		desktop.append("[Desktop Entry]")
		desktop.append("Encoding=UTF-8")
		desktop.append("Type=Application")
		desktop.append("Name=rgb_filter")
		desktop.append("Comment=Apply rgb filters")
		desktop.append("Exec={}".format(" ".join(cmd)))
		desktop.append("StartupNotify=false")
		desktop.append("Terminal=false")
		desktop.append("Hidden=false")
		home=os.environ.get("HOME")
		if home:
			wrkFile=os.path.join(home,".config","autostart","accesshelper_rgbFilter.desktop")
			if os.path.isdir(os.path.dirname(wrkFile))==False:
				os.makedirs(os.path.dirname(wrkFile))
			with open(wrkFile,"w") as f:
				f.write("\n".join(desktop))
	#def _generateAutostartDesktop

	def _removeAutostartDesktop(self):
		home=os.environ.get("HOME")
		if home:
			wrkFile=os.path.join(home,".config","autostart","accesshelper_rgbFilter.desktop")
			if os.path.isfile(wrkFile):
				self.changes=True
				self.refresh=True
				os.remove(wrkFile)
	#def _removeAutostartDesktop
