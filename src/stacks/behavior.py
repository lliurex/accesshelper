#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
from . import libaccesshelper
import gettext
_ = gettext.gettext
QString=type("")

i18n={
	"CONFIG":_("behavior"),
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
		self.dbg=False
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
		self.plasmaConfig={}
		self.wrkFiles=["kdeglobals","kwinrc"]
		self.wantSettings={"kwinrc":["FocusPolicy"]}
		self.blockSettings={"kdeglobals":["General"]}
		self.optionChanged=[]
		self.startup="false"
		self.accesshelper=libaccesshelper.accesshelper()
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
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		for kfile,sections in self.plasmaConfig.items():
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
						#btn.setStyleSheet(self.accesshelper.cssStyle())
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

		#self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		self.refresh=True
		config=self.getConfig()
		self.startup=config.get(self.level,{}).get("startup","false")
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		for kfile,sections in self.plasmaConfig.items():
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
		if self.startup=="true":
			self.showMsg(i18n.get("AUTOSTARTENABLED"))
			return
		plasmaConfig=self.plasmaConfig.copy()
		for kfile in self.wrkFiles:
			for section,data in plasmaConfig.get(kfile,{}).items():
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
				self.plasmaConfig[kfile][section]=dataTmp

		self.accesshelper.setPlasmaConfig(self.plasmaConfig)
		f=open("/tmp/accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		self.optionChanged=[]
		return

