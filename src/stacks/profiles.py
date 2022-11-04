#!/usr/bin/python3
import sys
import os,shutil
from PySide2.QtWidgets import QApplication,QLineEdit, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QListWidget,QFileDialog,QMessageBox
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
import subprocess
from . import libaccesshelper
_ = gettext.gettext
QString=type("")

i18n={
	"CONFIG":"profiles",
	"DESCRIPTION":_("Manage profiles"),
	"MENUDESCRIPTION":_("Load and save custom profiles"),
	"TOOLTIP":_("Use profile templates for quick configuration"),
	"SAVE":_("Save profile"),
	"LOAD":_("Load profile"),
	"REMOVE":_("Remove"),
	"DLG_REMOVE_TITLE":_("Confirm remove"),
	"DLG_REMOVE_TEXT":_("Remove profile"),
	"ERRORPERMS":_("Permission denied"),
	"ERRORDEFAULT":_("Default profiles could not be modified"),
	"ERRORREMOVE":_("Insuficient permissions for remove"),
	"SNAPSHOT_SYSTEM":_("Profile added to system's profiles"),
	"SNAPSHOT_USER":_("Profile added to user's profiles"),
	"RESTORESNAP":_("Profile loaded"),
	"IMPORT":_("Import profile"),
	"EXPORT":_("Export profile"),
	"PROFILE":_("Profile"),
	"RESTOREERROR":_("An error ocurred")
	}

class profiles(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('application-vnd.iccprofile')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=10
		self.enabled=True
		self.changed=[]
		self.config={}
		self.optionChanged=[]
		self.wrkDir="/usr/share/accesshelper/profiles"
		self.defaultDir="/usr/share/accesshelper/default"
		self.profilesPath={}
		self.lst_profiles=QListWidget()
		self.lst_userProfiles=QListWidget()
		self.onboardConf="onboard.dconf"
		self.hideControlButtons()
		self.accesshelper=libaccesshelper.accesshelper()
	#def __init__

	def _load_screen(self):
		self.setStyleSheet(self.accesshelper.cssStyle())
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.widgets={}
		self.refresh=True
		self.box.addWidget(self.lst_profiles,0,0,1,3)
		btn_load=QPushButton(i18n.get("LOAD"))
		self.box.addWidget(btn_load,1,0,1,1)
		btn_remove=QPushButton(i18n.get("REMOVE"))
		self.box.addWidget(btn_remove,1,1,1,1)
		btn_import=QPushButton(i18n.get("IMPORT"))
		self.box.addWidget(btn_import,1,2,1,1)
		self.inp_name=QLineEdit()
		self.box.addWidget(self.inp_name,2,0,1,1)
		btn_save=QPushButton(i18n.get("SAVE"))
		self.box.addWidget(btn_save,2,1,1,1,Qt.Alignment(1))
		btn_export=QPushButton(i18n.get("EXPORT"))
		self.box.addWidget(btn_export,2,2,1,1)

		self.lst_profiles.currentRowChanged.connect(self._updateText)
		btn_load.clicked.connect(self.loadProfile)
		btn_import.clicked.connect(self._importProfile)
		btn_remove.clicked.connect(self._removeProfile)
		btn_save.clicked.connect(self.writeConfig)
		btn_export.clicked.connect(self._exportProfile)
	#def _load_screen

	def _importProfile(self):
		dlg = QFileDialog(directory=os.environ.get('HOME'))
		dlg.setFileMode(QFileDialog.AnyFile)
		dlg.setNameFilters(["Tar files (*.tar)"])
		dlg.selectNameFilter("Tar files (*.tar)")
		if dlg.exec_():
			filenames = dlg.selectedFiles()
			if len(filenames):
				f=filenames[0]
				if self.level=='user':
					wrkUserDir=os.path.join(os.environ['HOME'],".config","accesshelper","profiles")
					self.accesshelper.importExportSnapshot(f,wrkUserDir)
				else:
					self.accesshelper.importExportSnapshot(f,self.wrkDir)
				self.updateScreen()
	#def _selectProfile

	def _exportProfile(self):
		name=self.inp_name.text()
		name=os.path.basename(name)
		if len(name)>20:
			name=name[0:19]
		nameProfile=self.profilesPath.get(name,'')
		if nameProfile=='':
			name="{}.tar".format(name)
			defName=os.path.join(os.environ.get('HOME',name))
			sourceName=self.profilesPath.get(name,'')
		if name:
			dlg = QFileDialog.getSaveFileName(self, i18n.get("EXPORT"),"{}".format(defName))
			f=dlg[0]
			if f:
				self.accesshelper.importExportSnapshot(sourceName,f)
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
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		name=self.inp_name.text()
		name=os.path.basename(name)
		if len(name)>20:
			name=name[0:19]
		name="{}.tar".format(name)
		sw=False
		if self.profilesPath.get(name,''):
			sw=self.accesshelper.restoreSnapshot(self.profilesPath.get(name))
		if sw:
			self.saveChanges('profile',name,level='user')
			self.showMsg(i18n.get("RESTORESNAP"))
		else:
			self.showMsg(i18n.get("RESTOREERROR"))
		self.refresh=True
		self.optionChanged=[]
		self._applyProfileSettings()
		cursor=QtGui.QCursor(Qt.PointingHandCursor)
		self.setCursor(cursor)
	#def loadProfile(self,*args):

	def _removeProfile(self,*args):
		self._debug("Removing profile")
		cursor=QtGui.QCursor(Qt.WaitCursor)
		self.setCursor(cursor)
		name=self.inp_name.text()
		name=os.path.basename(name)
		if len(name)>20:
			name=name[0:19]
		name="{}.tar".format(name)
		sw=False
		pfile=self.profilesPath.get(name,'')
		if pfile and os.path.isfile(pfile):
			dlg=QMessageBox(self)
			dlg.setWindowTitle(i18n.get("DLG_REMOVE_TITLE"))
			dlg.setText("{} {}?".format(i18n.get("DLG_REMOVE_TEXT"),self.inp_name.text()))
			dlg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
			dlg.setIcon(QMessageBox.Question)
			button = dlg.exec()
			if button == QMessageBox.Yes:
				try:
					os.remove(pfile)
				except:
					self.showMsg("{} {}".format(i18n.get("ERRORREMOVE"),self.inp_name.text()))
		cursor=QtGui.QCursor(Qt.PointingHandCursor)
		self.setCursor(cursor)
		self.updateScreen()
	#def loadProfile(self,*args):

	def _applyProfileSettings(self):
		self.config=self.getConfig("user",{}).get("user",{})
		if self.config.get('alpha',[])==[]:
			self.accesshelper.removeAutostartDesktop("accesshelper_rgbFilter.desktop")
		if self.config.get('startup','false')=='false':
			self.accesshelper.removeAutostartDesktop("accesshelper_profiler.desktop")
		if self.config.get('dock','false')=='false':
			self.accesshelper.removeAutostartDesktop("accessdock.desktop")
		self.accesshelper.setOnboardConfig()
		self._writeFileChanges()
	#def _applyProfileSettings

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
			appconfrc=os.path.join(os.path.dirname(self.wrkDir),"accesshelper.json")
			
		if self.accesshelper.takeSnapshot(profilePath,appconfrc)==False:
			self.showMsg("{}: {}".format(i18n.get("ERRORPERMS"),profilePath))
		else:
			if self.wrkDir in profilePath:
				self.showMsg("{}".format(i18n.get("SNAPSHOT_SYSTEM")))
			else:
				self.showMsg("{}".format(i18n.get("SNAPSHOT_USER")))
		self.updateScreen()

	def _writeFileChanges(self):
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			profile=self.config.get("profile","")
			if profile!="":
				f.write("{0}->{1}\n".format(i18n.get("PROFILE"),profile))

	#def _writeFileChanges(self):
