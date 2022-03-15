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
		self.wrkFiles=["kgammarc"]
		self.blockSettings={}
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
		def getRgbCompatValue(color):
			(top,color)=color
			c=round((color*top)/255,2)
			return c

		def adjustCompatValue(color):
			(multiplier,c,minValue)=color
			while (c*100)%multiplier!=0 and c!=0:
				c=round(c+0.01,2)
			if c<=minValue:
				c=minValue
			return c

		for name,wdg in self.widgets.items():
			if name=="alpha":
				alpha=wdg.currentColor()
				#xgamma uses 0.1-10 scale. Values>4 are too bright and values<0.5 too dark
				maxXgamma=3.5
				minXgamma=0.5
				#kgamma uses 0.40-3.5 scale. 
				maxKgamma=3.5
				minKgamma=0.4
				(xred,xblue,xgreen)=map(getRgbCompatValue,[(maxXgamma,alpha.red()),(maxXgamma,alpha.blue()),(maxXgamma,alpha.green())])
				(red,blue,green)=map(getRgbCompatValue,[(maxKgamma,alpha.red()),(maxKgamma,alpha.blue()),(maxKgamma,alpha.green())])
				if red+blue+green>(maxKgamma*(2-(maxKgamma*0.10))): #maxKGamma*2=at least two channel very high, plus a 10% margin
					red-=1
					green-=1
					blue-=1
				multiplier=1
				(xred,xblue,xgreen)=map(adjustCompatValue,[[multiplier,minXgamma,xred],[multiplier,minXgamma,xblue],[multiplier,minXgamma,xgreen]])
				multiplier=5
				(red,blue,green)=map(adjustCompatValue,[[multiplier,minKgamma,red],[multiplier,minKgamma,blue],[multiplier,minKgamma,green]])
				brightness=1
				self.sysConfig['kgammarc']['ConfigFile']=[("use","kgammarc")]
				self.sysConfig['kgammarc']['SyncBox']=[("sync","yes")]
				values=[]
				for gamma in self.sysConfig['kgammarc']['Screen 0']:
					(desc,value)=gamma
					if desc=='bgamma':
						values.append((desc,"{0:.2f}".format(blue)))
					elif desc=='rgamma':
						values.append((desc,"{0:.2f}".format(red)))
					elif desc=='ggamma':
						values.append((desc,"{0:.2f}".format(green)))
				self.sysConfig['kgammarc']['Screen 0']=values
			####for monitor in self._getMonitors():
			####	xrand=["xrandr","--output",monitor,"--gamma","{0}:{1}:{2}".format(alpha.red()/25.5,alpha.green()/25.5,alpha.blue()/25.5),"--brightness","{}".format(brightness)]
				xgamma=["xgamma","-screen","0","-rgamma","{0:.2f}".format(xred),"-ggamma","{0:.2f}".format(xgreen),"-bgamma","{0:.2f}".format(xblue)]
				print(xgamma)
				cmd=subprocess.run(xgamma,capture_output=True,encoding="utf8")
				print(cmd.stderr)
		functionHelper.setSystemConfig(self.sysConfig)
		self.optionChanged=[]
		self.refresh=True
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
	#def writeConfig

	def _reset_screen(self,*args):
		for monitor in self._getMonitors():
			xrand=["xrandr","--output",monitor,"--gamma","1:1:1","--brightness","1"]
		xgamma=["xgamma","-screen","0","-rgamma","1","-ggamma","1","-bgamma","1"]
		cmd=subprocess.run(xgamma,capture_output=True,encoding="utf8")
		values=[("ggamma","1.00"),("bgamma","1.00"),("rgamma","1.00")]
		self.sysConfig['kgammarc']['Screen 0']=values
		functionHelper.setSystemConfig(self.sysConfig)
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
