#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
from . import functionHelper
import gettext
_ = gettext.gettext
QString=type("")

i18n={
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Desktop behavior"),
	"MENUDESCRIPTION":_("Configure how desktop works"),
	"TOOLTIP":_("Set many options related with desktop behavior"),
	"FOCUSCLICK":_("Click to focus"),
	"FOCUSFOLLOW":_("Focus follows pointer"),
	"SINGLECLICK":_("Only one click for open elements"),
	"SCROLLBARLEFTCLICKNAVIGATESBYPAGE":_("Click on scrollbar moves to position"),
	"SCROLLBARMODE":_("Scrollbar sliding mode"),
	"GRIDONMOVE":_("Show a grid when moving windows"),
	"HOTCORNERS":_("Actions on top left screen corner"),
	"RESOLUTION":_("Set screen resolution"),
	"FOCUSPOLICY":_("Focus follows pointer")
	}

class behavior(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("behavior load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('application-x-desktop')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=2
		self.enabled=False
		self.defaultRepos={}
		self.changed=[]
		self.level='user'
		self.config={}
		self.sysConfig={}
		self.wrkFiles=["kdeglobals","kwinrc"]
		self.wantSettings={"kwinrc":["FocusPolicy"]}
		self.blockSettings={"kdeglobals":["General"]}
		self.optionChanged=[]
	#def __init__

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._updateConfig)
		self.widgets={}
		self.level='user'
		self.refresh=True
		row,col=(0,0)
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile)
			self.sysConfig.update(systemConfig)
		for kfile,sections in self.sysConfig.items():
			want=self.wantSettings.get(kfile,[])
			block=self.blockSettings.get(kfile,[])
			for section,settings in sections.items():
				if section in block and len(want)==0:
					continue
				for setting in settings:
					(name,data)=setting
					if name in block or (len(want)>0 and name not in want):
						continue
					desc=i18n.get(name.upper(),name)
					lbl=QLabel(desc)
					#if (data.lower() in ("true","false")) or (data==''):
					if (isinstance(data,str)):
						btn=QCheckBox(desc)
						#btn=QPushButton(desc)
						#btn.setStyleSheet(functionHelper.cssStyle())
						#btn.setAutoDefault(False)
						#btn.setDefault(False)
						#btn.setCheckable(True)
						state=False
						self.widgets.update({name:btn})
						self.box.addWidget(btn,row,col)
					col+=1
					if col==1:
						row+=1
						col=0

		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile)
			self.sysConfig.update(systemConfig)
		for kfile,sections in self.sysConfig.items():
			want=self.wantSettings.get(kfile,[])
			block=self.blockSettings.get(kfile,[])
			for section,settings in sections.items():
				if section in block and len(want)==0:
					continue
				for setting in settings:
					(name,data)=setting
					if name in block or (len(want)>0 and name not in want):
						continue
					desc=i18n.get(name.upper(),name)
					lbl=QLabel(desc)
					#if (data.lower() in ("true","false")) or (data==''):
					if (isinstance(data,str)):
						btn=self.widgets.get(name,'')
						if btn:
							state=False
							if data.lower()=="true" or data.lower()=="focusfollowsmouse":
								state=True
							btn.setChecked(state)
	#def _udpate_screen

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		sysConfig=self.sysConfig.copy()
		for kfile in self.wrkFiles:
			for section,data in sysConfig.get(kfile,{}).items():
				dataTmp=[]
				for setting,value in data:
					btn=self.widgets.get(setting,'')
					if isinstance(btn,QCheckBox):
						value=btn.isChecked()
						desc=btn.text()
						if desc==i18n.get("FOCUSPOLICY",''):
							if value:
								value="FocusFollowsMouse"
							else:
								value=""
						elif value:
							value="true"
						else:
							value="false"
					dataTmp.append((setting,value))
				self.sysConfig[kfile][section]=dataTmp

		functionHelper.setSystemConfig(self.sysConfig)
		f=open("/tmp/accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		self.optionChanged=[]
		return

