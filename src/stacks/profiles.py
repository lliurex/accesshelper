#!/usr/bin/python3
import sys
import os,shutil
from PySide2.QtWidgets import QApplication,QLineEdit, QLabel, QWidget, QPushButton,QVBoxLayout,QLineEdit,QHBoxLayout,QListWidget
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
import subprocess
from . import functionHelper
_ = gettext.gettext
QString=type("")

i18n={
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Manage profiles"),
	"MENUDESCRIPTION":_("Load and save custom profiles"),
	"TOOLTIP":_("Use profile templates for quick configuration"),
	"SAVE":_("Save profile"),
	"LOAD":_("Load profile"),
	"ERRORPERMS":_("Permission denied"),
	"SNAPSHOT_SYSTEM":_("Profile added to system's profiles"),
	"SNAPSHOT_USER":_("Profile added to user's profiles"),
	"RESTORESNAP":_("Profile loaded"),
	"RESTOREERROR":_("An error ocurred")
	}

class profiles(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("access Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('application-vnd.iccprofile')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=5
		self.enabled=True
		self.changed=[]
		self.config={}
		self.optionChanged=[]
		self.wrkDir="/usr/share/accesshelper/profiles"
		self.defaultDir="/usr/share/accesshelper/default"
		self.profilesPath={}
		self.lst_profiles=QListWidget()
		self.lst_userProfiles=QListWidget()
		self.hideControlButtons()
	#def __init__

	def _load_screen(self):
		self.setStyleSheet(functionHelper.cssStyle())
		self.box=QVBoxLayout()
		self.setLayout(self.box)
		self.widgets={}
		self.refresh=True
		self.box.addWidget(self.lst_profiles)
		btn_load=QPushButton(i18n.get("LOAD"))
		self.box.addWidget(btn_load)
		btn_save=QPushButton(i18n.get("SAVE"))
		self.inp_name=QLineEdit()
		wdg_save=QWidget()
		hbox=QHBoxLayout()
		wdg_save.setLayout(hbox)
		hbox.addWidget(self.inp_name)
		hbox.addWidget(btn_save)
		self.box.addWidget(wdg_save)

		self.lst_profiles.currentRowChanged.connect(self._updateText)
		btn_load.clicked.connect(self.loadProfile)
		btn_save.clicked.connect(self.writeConfig)
		self.updateScreen()
	#def _load_screen

	def _updateText(self,*args):
		widget=self.lst_profiles.currentItem()
		if widget:
			bg=widget.background()
			fProfile=widget.text()
			self.inp_name.setText(fProfile)
	#def _updateText

	def updateScreen(self):
		self.profilesPath={}
		self.lst_profiles.clear()
		wrkUserDir=os.path.join(os.environ['HOME'],".config","accesshelper","profiles")
		add=[]
		wrkDirs=[self.defaultDir,self.wrkDir,wrkUserDir]
		for wrkDir in wrkDirs:
			if os.path.isdir(wrkDir):
				flist=os.listdir(wrkDir)
				flist.sort()
				for f in flist:
					if len(f)>50:
						f=f[0:49]
					if f not in self.profilesPath.keys():
						self.lst_profiles.addItem(f.rstrip(".tar"))
						add.append(f)
						self.profilesPath.update({f:os.path.join(wrkDir,f)})
						item=self.lst_profiles.item(self.lst_profiles.count()-1)
						font=item.font()
						font.setStretch(120)
						if wrkDir==self.wrkDir or wrkDir==self.defaultDir:
							font.setBold(True)
							if wrkDir==self.defaultDir:
								font.setItalic(True)
						#	if font.pointSize()<14:
						#		font.setPointSize(14)
						item.setFont(font)
	#def _udpate_screen

	def loadProfile(self,*args):
		self._debug("Restoring snapshot")
		name=self.inp_name.text()
		name=os.path.basename(name)
		if len(name)>20:
			name=name[0:19]
		name="{}.tar".format(name)
		sw=False
		if self.profilesPath.get(name,''):
			sw=functionHelper.restore_snapshot(self.profilesPath.get(name))
		if sw:
			self.saveChanges('profile',name,level='user')
			self.showMsg(i18n.get("RESTORESNAP"))
		else:
			self.showMsg(i18n.get("RESTOREERROR"))
		self.refresh=True
		self.optionChanged=[]

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		self._debug("Taking snapshot")
		name=self.inp_name.text()
		name=os.path.basename(name)
		if len(name)>20:
			name=name[0:19]
		wrkDir=self.wrkDir
		self.optionChanged=[]
		if self.profilesPath.get(name,''):
			wrkDir=os.path.basename(self.profilesPath.get(name,''))
		appconfrc=os.path.join(os.path.dirname(wrkDir),"appconfrc")
			
		if functionHelper.take_snapshot(wrkDir,name,appconfrc=appconfrc)==False:
			self.showMsg("{}: {}".format(i18n.get("ERRORPERMS"),wrkDir))
		else:
			if wrkDir==self.wrkDir:
				self.showMsg("{}".format(i18n.get("SNAPSHOT_SYSTEM")))
			else:
				self.showMsg("{}".format(i18n.get("SNAPSHOT_USER")))
		self.updateScreen()
		

