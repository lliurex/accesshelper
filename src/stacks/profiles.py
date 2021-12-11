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
	"SNAPSHOT_USER":_("Profile added to user's profiles")
	}

class profiles(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("access Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('application-vnd.iccprofile')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=11
		self.enabled=True
		self.changed=[]
		self.config={}
		self.optionChanged=[]
		self.wrkDir="/usr/share/accesshelper/profiles"
		self.lst_profiles=QListWidget()
		self.hideControlButtons()
	#def __init__

	def _load_screen(self):
		self.box=QVBoxLayout()
		self.setLayout(self.box)
		self.widgets={}
		self.level='user'
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
		self.lst_profiles.clear()
		add=[]
		if os.path.isdir(self.wrkDir):
			for f in os.listdir(self.wrkDir):
				if len(f)>20:
					f=f[0:19]
				if f not in add:
					self.lst_profiles.addItem(f)
					add.append(f)
					item=self.lst_profiles.item(self.lst_profiles.count()-1)
					brush=QtGui.QBrush(QtGui.QColor("orange"),Qt.Dense4Pattern)
					item.setBackground(brush)
		self.lst_profiles.sortItems()

		wrkUserDir=os.path.join(os.environ['HOME'],".config","accesshelper","profiles")
		if os.path.isdir(wrkUserDir):
			for f in os.listdir(wrkUserDir):
				if len(f)>20:
					f=f[0:19]
				if f not in add:
					self.lst_profiles.addItem(f)
					add.append(f)
	#def _udpate_screen

	def loadProfile(self,*args):
		self._debug("Restoring snapshot")
		name=self.inp_name.text()
		name=os.path.basename(name)
		if len(name)>20:
			name=name[0:19]
		self.restore_snapshot(self.wrkDir,name)
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
		if len(self.lst_profiles.findItems(name,Qt.MatchExactly))==0:
			wrkDir=os.join.path(os.environ.get("HOME"),".config","accesshelper","profiles")
		else:
			widget=self.lst_profiles.findItems(name,Qt.MatchExactly)[0]
			if widget.background().style()==Qt.NoBrush:
				wrkDir=os.path.join(os.environ.get("HOME"),".config","accesshelper","profiles")
		if self.take_snapshot(wrkDir,name)==False:
			self.showMsg("{}: {}".format(i18n.get("ERRORPERMS"),wrkDir))
		else:
			if wrkDir==self.wrkDir:
				self.showMsg("{}".format(i18n.get("SNAPSHOT_SYSTEM")))
			else:
				self.showMsg("{}".format(i18n.get("SNAPSHOT_USER")))
		self.optionChanged=[]
		self.updateScreen()

	def take_snapshot(self,wrkDir,snapshotName=''):
		if snapshotName=='':
			snapshotName="test"
		self._debug("Take snapshot {}".format(snapshotName))
		destPath=os.path.join(wrkDir,snapshotName)
		self._debug("Destination {}".format(destPath))


		sw=True
		for kfile in functionHelper.dictFileData.keys():
			kPath=os.path.join(os.environ['HOME'],".config",kfile)
			if os.path.isfile(kPath):
				destFile=os.path.join(destPath,kfile)
				if os.path.isdir(destPath)==False:
					if os.path.isfile(destPath):
						destPath="_1".format(destPath)
						destFile=os.path.join(destPath,kfile)
					try:
						os.makedirs(destPath)
					except:
						sw=False
				try:
					shutil.copy(kPath,destFile)
					self._debug("Copying {0}->{1}".format(kPath,destFile))
				except:
					cmd=["pkexec","/usr/share/accesshelper/helper/profiler.sh",kPath,destFile]
					try:
						subprocess.run(cmd)
					except Exception as e:
						self._debug(e)
						self._debug("Permission denied for {}".format(destPath))
						sw=False
					break
		return sw
	#def take_snapshot
			
	def restore_snapshot(self,wrkDir,snapshotName):
		snapPath=os.path.join(wrkDir,snapshotName)
		if os.path.isdir(snapPath)==True:
			config=functionHelper.getSystemConfig(sourceFolder=snapPath)
			for kfile,sections in config.items():
				for section,data in sections.items():
					for (desc,value) in data:
						functionHelper._setKdeConfigSetting(section,desc,value,kfile)
		self.refresh=True
	#def restore_snapshot
