#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QListWidget,QSizePolicy
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import json
import subprocess
import dbus,dbus.service,dbus.exceptions
from . import functionHelper
QString=type("")

i18n={
	"COLOURS":_("Colours"),
	"FONTS":_("Fonts"),
	"CURSOR":_("Cursor"),
	"AIDS":_("Visual Aids"),
	"SCREEN":_("Screen Options"),
	"HOTKEYS":_("Keyboard Shortcuts"),
	"ACCESSIBILITY":_("Accessibility options"),
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Accessibility configuration"),
	"MENUDESCRIPTION":_("Set accesibility options"),
	"TOOLTIP":_("From here you can activate/deactivate accessibility aids"),
	"HIGHCONTRAST":_("Enable high contrast palette"),
	"INVERTENABLED":_("Invert screen colours"),
	"INVERTWINDOW":_("Invert windows colours"),
	"ANIMATEONCLICK":_("Show animation on click"),
	"FOCUSFOLLOWSMOUSE":_("Follow cursor"),
	"CLICKTOFOCUS":_("Click to focus"),
	"SIZE":_("Font size"),
	"FAMILY":_("Font family"),
	"CURSORTHEME":_("Cursor theme"),
	"CURSORSIZE":_("Cursor size"),
	"FOLLOWPOINTER":_("Always follow the pointer"),
	"SINGLECLICK":_("Only one click for open elements"),
	"SCROLLBARMODE":_("Scrollbar sliding mode"),
	"SHOWDESKTOPGRID":_("Show a grid when moving windows"),
	"LOOKINGGLASSENABLED":_("Activate eyefish effect"),
	"MAGNIFIERENABLED":_("Activate glass effect"),
	"ZOOMDESKTOP":_("Zoom desktop"),
	"HOTCORNERS":_("Actions on screen corners"),
	"SYSTEMBELL":_("Acoustic system bell"),
	"FOCUSPOLICY":_("Set the policy focus")
	}

class access(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("access Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-accessibility')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=1
		self.enabled=True
		self.defaultRepos={}
		self.changed=[]
		self.level='user'
		self.bus=None
		self.config={}
		self.sysConfig={}
		#self.kwinMethods=self._getKwinMethods()
		self.wrkFiles=["kwinrc"]
		self.blockSettings={"kwinrc":["FocusPolicy"]}
		self.wantSettings={}
		self.widgets={}
		self.kwinMethods={}
		self.kaccessSections={"SystemBell":"Bell","invertEnabled":"Plugins","SingleClick":"KDE"}
		self.fileSections={"Bell":"kaccessrc","Plugins":"kwinrc","KDE":"kdeglobals"}
		self.optionChanged=[]
	#def __init__

	def cssStyle(self):
		style="""
			QLabel{
				margin:96px;
				margin-right:6px;
			}
			QCheckBox{
				margin:13px;
			}
		"""
		return(style)

	def _load_screen(self):
		self.box=QVBoxLayout()
		self.setLayout(self.box)
		self.refresh=True
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile)
			self.sysConfig.update(systemConfig)
			for kfile,sections in systemConfig.items():
				for section,settings in sections.items():
					for setting in settings:
						(name,data)=setting
						want=self.wantSettings.get(kfile,[])
						block=self.blockSettings.get(kfile,[])
						if name in block or (len(want)>0 and name not in want):
							continue
						desc=i18n.get(name.upper(),name)
						lbl=QLabel(desc)
						if (data.lower() in ("true","false")) or (data==''):
							btn=QCheckBox(desc)
							state=False
							if data.lower()=="true":
								state=True
							btn.setChecked(state)
							self.box.addWidget(btn)
							self.widgets.update({name:btn})
						#ibtn.clicked
		#lst_settings.resizeRowsToContents()
		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		return
	#def _udpate_screen

	def _updateConfig(self,*args):
		return
	def writeConfig(self):
		sysConfig=self.sysConfig.copy()
		for kfile in self.wrkFiles:
			for section,data in sysConfig.get(kfile,{}).items():
				dataTmp=[]
				for setting,value in data:
					btn=self.widgets.get(setting,'')
					if btn:
						value=btn.isChecked()
						if value:
							value="true"
						else:
							value="false"
					dataTmp.append((setting,value))
				self.sysConfig[kfile][section]=dataTmp

		functionHelper.setSystemConfig(self.sysConfig)
		return
		for section,option in self.config.get(self.level,{}).items():
			if isinstance(option,dict):
				for name,value in option.items():
					if name in self.optionChanged:
						if name in self.kaccessSections:
							self._debug("Setting {} -> {}".format(name,value))
							self._setKdeConfigSetting(group=self.kaccessSections.get(name),key=name,value=value)
						#self._exeKwinMethod(name) 
		self._reloadConfig()
		self.optionChanged=[]

