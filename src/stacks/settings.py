#!/usr/bin/python3
import sys
import os
import shutil
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QGridLayout,QComboBox,QCheckBox
from PySide2 import QtGui
from PySide2.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack
from . import libaccesshelper
from . import libhotkeys
import subprocess
import tempfile
import gettext
_ = gettext.gettext
QString=type("")

i18n={
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Manage application"),
	"MENUDESCRIPTION":_("Configure some options"),
	"TOOLTIP":_("Set config level, default template.."),
	"AUTOSTART":_("Autostart enabled for user"),
	"DISABLEAUTOSTART":_("Autostart disabled for user"),
	"AUTOSTARTERROR":_("Autostart could not be disabled"),
	"ENABLEDOCK":_("Enabled accessibilty dock with hotkey"),
	"DISABLEDOCK":_("Disabled accessibilty dock"),
	"VOICESPEED":_("Voice speed when reading"),
	"VOICEPITCH":_("Voice pitch")
	}

class settings(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("settings Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('systemsettings')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=11
		self.enabled=True
		self.changed=[]
		self.config={}
		self.widgets={}
		self.wrkDirs=["/usr/share/accesshelper/profiles","/usr/share/accesshelper/default",os.path.join(os.environ.get('HOME'),".config/accesshelper/profiles")]
		self.profilerAuto="accesshelper_profiler.desktop"
		self.dockAuto="accessdock.desktop"
		self.optionChanged=[]
		self.keymap={}
		for key,value in vars(Qt).items():
			if isinstance(value, Qt.Key):
				self.keymap[value]=key.partition('_')[2]
		self.modmap={
					Qt.ControlModifier: self.keymap[Qt.Key_Control],
					Qt.AltModifier: self.keymap[Qt.Key_Alt],
					Qt.ShiftModifier: self.keymap[Qt.Key_Shift],
					Qt.MetaModifier: self.keymap[Qt.Key_Meta],
					Qt.GroupSwitchModifier: self.keymap[Qt.Key_AltGr],
					Qt.KeypadModifier: self.keymap[Qt.Key_NumLock]
					}
		self.accesshelper=libaccesshelper.accesshelper()
	#def __init__

	def _load_screen(self):
		def _change_osh():
			idx=self.cmb_level.currentIndex()
			if idx==0:
				lbl_help.setText(_("The config will be applied per user"))
			elif idx==1:
				lbl_help.setText(_("The config will be applied to all users"))
			elif idx==2:
				lbl_help.setText(_("The config will be applied to all users and clients"))
			self.fakeUpdate()
		self.installEventFilter(self)
		box=QGridLayout()
		lbl_txt=QLabel(_("Choose the config level that should use the app"))
		box.addWidget(lbl_txt,0,0,1,1)
		self.cmb_level=QComboBox()
		self.cmb_level.addItem(_("User"))
		self.cmb_level.addItem(_("System"))
		self.cmb_level.addItem(_("N4d"))
		self.cmb_level.activated.connect(_change_osh)
		self.cmb_level.setFixedWidth(100)
		box.addWidget(self.cmb_level,0,1,1,1)
		self.widgets.update({self.cmb_level:'config'})
		lbl_help=QLabel("")
		lbl_help.setAlignment(Qt.AlignTop)
		box.addWidget(lbl_help,1,0,1,2,Qt.AlignTop|Qt.AlignCenter)
		box.addWidget(QLabel(_("Session settings")),2,0,1,2,Qt.AlignTop)
		chk_template=QCheckBox(_("Load template on start"))
		box.addWidget(chk_template,3,0,1,1,Qt.AlignTop)
		self.widgets.update({chk_template:'startup'})
		cmb_template=QComboBox()
		self.widgets.update({cmb_template:'profile'})
		box.addWidget(cmb_template,3,1,1,1,Qt.AlignTop)
		chk_dock=QCheckBox(_("Enable accesshelper dock"))
		box.addWidget(chk_dock,4,0,1,1,Qt.AlignTop)
		self.widgets.update({chk_dock:'dock'})
		(mainHk,hkData,hkSetting,hkSection)=self.accesshelper.getHotkey("accessdock.desktop")
		if mainHk=="":
			mainHk="Ctrl+Space"
		self.btn_dockHk=libhotkeys.QHotkeyButton(mainHk)
		self.btn_dockHk.hotkeyAssigned.connect(self._testHotkey)
		box.addWidget(self.btn_dockHk,4,1,1,1,Qt.AlignTop)
		self.widgets.update({self.btn_dockHk:'dockHk'})
		box.setRowStretch(0,1)
		for i in range (1,4):
			box.setRowStretch(i,0)
		box.setRowStretch(i+1,2)
		for wrkDir in self.wrkDirs:
			if os.path.isdir(wrkDir):
				for f in os.listdir(wrkDir):
					cmb_template.addItem("{}".format(f))
		cmb_template.setCurrentText("default")
		self.setLayout(box)
		_change_osh()
		return(self)
	#def _load_screen

	def _testHotkey(self,hotkey):
		self._debug("Read Hotkey {} from {}".format(hotkey,self.btn_dockHk))
		if not hotkey.get("action","")=="":
			try:
				self.showMsg("{0} {1} {2}".format(hotkey.get("hotkey"),i18n.get("HKASSIGNED"),hotkey.get("action")))
			except:
				pass
			self.btn_dockHk.revertHotkey()
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
	#def _testHotkey

	def fakeUpdate(self):
		idx=self.cmb_level.currentIndex()
		level='user'
		if idx==0:
			level='user'
		elif idx==1:
			level='system'
		elif idx==2:
			level='n4d'
		self.cmb_level.setCurrentIndex(idx)
	#	self.updateScreen()
	#def fakeUpdate

	def _getAutostartFile(self,f):
		autostartFiles={}
		if os.path.isfile(os.path.join(os.environ.get('HOME'),".config/autostart/","{}".format(f))):
			autostartFiles['user']=os.path.join(os.environ.get('HOME'),".config/autostart/","{}".format(f))
			autostartFiles['enabled']=True
		if os.path.isfile(os.path.join("/etc/xdg/autostart/","{}".format(f))):
			autostartFiles['system']=os.path.join("/etc/xdg/autostart/","{}".format(f))
			autostartFiles['enabled']=True
		return(autostartFiles)
	#def _getAutostartFile

	def updateScreen(self,level=None):
		config=self.getConfig(level)
		level=self.level
		profile=''
		if level in config.keys():
			profile=config[level].get('profile','')
			speed=config[level].get('speed','1x')
			pitch=config[level].get('pitch','50')
		startup=False
		if self._getAutostartFile(self.profilerAuto).get('enabled'):
			startup=True
		dock=False
		if self._getAutostartFile(self.dockAuto).get('enabled'):
			dock=True
		for widget,desc in self.widgets.items():
			if desc=="startup":
				widget.setChecked(startup)
			elif desc=="profile":
				widget.setCurrentText(profile)
			elif desc=="speed":
				widget.setCurrentText(speed)
			elif desc=="pitch":
				widget.setCurrentText(pitch)
			elif desc=="config":
				if level=="user":
					idx=0
				elif level=="system":
					idx=1
				elif level=="n4d":
					idx=2
				widget.setCurrentIndex(idx)
			elif desc=="dock":
				widget.setChecked(dock)
	#def _udpate_screen

	def _updateConfig(self,key):
		pass
	#def _updateConfig

	def writeConfig(self):
		startWdg=None
		profile=''
		config=self.getConfig()
		for widget,desc in self.widgets.items():
			if desc=="startup":
				startWdg=widget
			if desc=="dock":
				dockWdg=widget
			if desc=="dockHk":
				dockHk=widget
			if isinstance(widget,QCheckBox):
				value=widget.isChecked()
				if value:
					value="true"
				else:
					value="false"
			elif isinstance(widget,QComboBox):
				if desc=="config":
					value=widget.currentIndex()
					if value==0:
						value="user"
					elif value==1:
						value="system"
					elif value==2:
						value="n4d"
					self.saveChanges(desc,value,level="user")
				else:
					value=widget.currentText()
					if desc=="profile":
						profile=value
			self.saveChanges(desc,value)
		if startWdg:
			if startWdg.isChecked():
				self._setAutostart(profile)
			else:
				self._removeAutostart(profile)
		if dockWdg:
			if dockWdg.isChecked():
				self._setAutostartDock()
				self.saveChanges("dockHk",dockHk.text(),level="user")
			else:
				self._removeAutostartDock()
				self.saveChanges("dockHk","",level="user")
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
		self.changes=""
		self.refresh=True
	#def writeConfig

	def _setAutostart(self,profile):
		if profile:
			tmpHdl,tmpF=tempfile.mkstemp()
			tmpf=open(tmpF,'w')
			fprof=os.path.join("/usr/share/accesshelper/helper/",self.profilerAuto)
			with open(fprof,"r") as f:
				lines=f.readlines()
				for line in lines:
					if line.startswith("Exec="):
						profile="{} init".format(profile)
						line=line.replace("%u",profile)
					tmpf.write(line)
			tmpf.close()
			destPath=os.path.join(os.environ.get("HOME"),".config/autostart/",self.profilerAuto)
			if os.path.isdir(os.path.dirname(destPath))==False:
				os.makedirs(os.path.dirname(destPath))
			shutil.copy(tmpF,destPath)
			self.showMsg("{} {}".format(i18n.get("AUTOSTART"),os.environ.get("USER")))
	#def _setAutostart

	def _removeAutostart(self,profile):
		autoFiles=self._getAutostartFile(self.profilerAuto)
		if os.path.isfile(autoFiles.get('user',''))==True:
			try:
				os.remove(autoFiles['user'])
				self.showMsg("{} {}".format(i18n.get("DISABLEAUTOSTART"),os.environ.get("USER")))
			except:
				self.showMsg(i18n.get("AUTOSTARTERROR"))
	#def _removeAutostart

	def _setAutostartDock(self):
		destPath=os.path.join(os.environ.get("HOME"),".config/autostart/accessdock.desktop")
		if os.path.isdir(os.path.dirname(destPath))==False:
			os.makedirs(os.path.dirname(destPath))
		tmpF="/usr/share/applications/accessdock.desktop"
		shutil.copy(tmpF,destPath)
		btnHk="Ctrl+Space"
		for widget in self.widgets.keys():
			if isinstance(widget,libhotkeys.QHotkeyButton):
				btnHk=widget.text()
				break
		hotkey=btnHk
		desc="{0},{0},show accessdock".format(hotkey)
		data=[("_launch",desc),("_k_friendly_name","accessdock")]
		config={'kglobalshortcutsrc':{'accessdock.desktop':data}}
		self.accesshelper.setPlasmaConfig(config)
		self.showMsg("{0} {1}".format(i18n.get("ENABLEDOCK"),hotkey))

	def _removeAutostartDock(self):
		autoFiles=self._getAutostartFile(self.dockAuto)
		hotkey=""
		desc="{0},{0},show accessdock".format(hotkey)
		data=[("_launch",""),("_k_friendly_name","")]
		config={'kglobalshortcutsrc':{'accessdock.desktop':data}}
		self.accesshelper.setPlasmaConfig(config)
		if os.path.isfile(autoFiles.get('user',''))==True:
			try:
				os.remove(autoFiles.get('user'))
				self.showMsg("{}".format(i18n.get("DISABLEDOCK")))
			except:
				self.showMsg(i18n.get("AUTOSTARTERROR"))
	#def _removeAutostart

