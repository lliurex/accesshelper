#!/usr/bin/python3
import sys
import os,shutil
from PySide2.QtWidgets import QApplication,QLineEdit, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QListWidget,QFileDialog
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
	"ERRORDEFAULT":_("Default profiles could not be modified"),
	"SNAPSHOT_SYSTEM":_("Profile added to system's profiles"),
	"SNAPSHOT_USER":_("Profile added to user's profiles"),
	"RESTORESNAP":_("Profile loaded"),
	"IMPORT":_("Import profile"),
	"EXPORT":_("Export profile"),
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
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.widgets={}
		self.refresh=True
		self.box.addWidget(self.lst_profiles,0,0,1,3)
		btn_load=QPushButton(i18n.get("LOAD"))
		self.box.addWidget(btn_load,1,0,1,2)
		btn_import=QPushButton(i18n.get("IMPORT"))
		btn_import.clicked.connect(self._importProfile)
		self.box.addWidget(btn_import,1,2,1,1)
		self.inp_name=QLineEdit()
		self.box.addWidget(self.inp_name,2,0,1,1)
		btn_save=QPushButton(i18n.get("SAVE"))
		self.box.addWidget(btn_save,2,1,1,1,Qt.Alignment(1))
		btn_export=QPushButton(i18n.get("EXPORT"))
		btn_export.clicked.connect(self._exportProfile)
		self.box.addWidget(btn_export,2,2,1,1)

		self.lst_profiles.currentRowChanged.connect(self._updateText)
		btn_load.clicked.connect(self.loadProfile)
		btn_save.clicked.connect(self.writeConfig)
		self.updateScreen()
	#def _load_screen

	def _importProfile(self):
		dlg = QFileDialog()
		dlg.setFileMode(QFileDialog.AnyFile)
		dlg.setNameFilters(["Tar files (*.tar)"])
		dlg.selectNameFilter("Tar files (*.tar)")
		if dlg.exec_():
			filenames = dlg.selectedFiles()
			if len(filenames):
				f=filenames[0]
				if self.level=='user':
					wrkUserDir=os.path.join(os.environ['HOME'],".config","accesshelper","profiles")
					functionHelper.importExportSnapshot(f,wrkUserDir)
				else:
					functionHelper.importExportSnapshot(f,self.wrkDir)
				self.updateScreen()
	#def _selectProfile

	def _exportProfile(self):
		name=self.inp_name.text()
		name=os.path.basename(name)
		if len(name)>20:
			name=name[0:19]
		name=self.profilesPath.get(name,'')
		if name=='':
			name="{}.tar".format(name)
			name=self.profilesPath.get(name,'')
		if name:
			dlg = QFileDialog.getSaveFileName(self, i18n.get("EXPORT"),"{}".format(name))
			f=dlg[0]
			if f:
				functionHelper.importExportSnapshot(name,f)
	#def _exportProfile


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
						self.lst_profiles.addItem(f.replace(".tar",""))
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
			sw=functionHelper.restoreSnapshot(self.profilesPath.get(name))
		if sw:
			self.saveChanges('profile',name,level='user')
			self.showMsg(i18n.get("RESTORESNAP"))
		else:
			self.showMsg(i18n.get("RESTOREERROR"))
		self.refresh=True
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		self.optionChanged=[]

	def _updateConfig(self,key):
		pass

	def writeConfig(self,system=False):
		self._debug("Taking snapshot")
		self.config=self.getConfig("system",{}).get("system",{})
		self.level=self.config.get('config')
		name=self.inp_name.text()
		name=os.path.basename(name)
		if len(name)>50:
			name=name[0:49]

		if name.endswith(".tar")==False:
			name="{}.tar".format(name)
		if os.path.isdir(self.defaultDir)==True:
			if name in os.listdir(self.defaultDir):
				self.showMsg("{}".format(i18n.get("ERRORDEFAULT")))
				self.optionChanged=[]
				return
		profilePath=self.profilesPath.get(name,'')
		if profilePath=='':
			if self.level=='user':
				profilePath=os.path.join(os.environ.get('HOME'),".config/accesshelper/profiles","{}".format(name))
			else:
				profilePath=os.path.join(self.wrkDir,"{}".format(name))
		if self.level=='user':
			appconfrc=os.path.join(os.environ.get('HOME'),".config/accesshelper/accesshelper.json")
		else:
			appconfrc=os.path.join(self.path.dirname(self.wrkDir),"accesshelper.json")
			
		if functionHelper.takeSnapshot(profilePath,appconfrc=appconfrc)==False:
			self.showMsg("{}: {}".format(i18n.get("ERRORPERMS"),profilePath))
		else:
			if self.wrkDir in profilePath:
				self.showMsg("{}".format(i18n.get("SNAPSHOT_SYSTEM")))
			else:
				self.showMsg("{}".format(i18n.get("SNAPSHOT_USER")))
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		self.optionChanged=[]
		self.updateScreen()
		
