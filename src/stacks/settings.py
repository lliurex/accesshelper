#!/usr/bin/python3
import sys
import os
import shutil
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QGridLayout,QComboBox,QCheckBox
from PySide2 import QtGui
from PySide2.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack
from . import libaccesshelper
from appconfig import appconfigControls
import subprocess
import tempfile
import gettext
_ = gettext.gettext
QString=type("")

i18n={
	"CONFIG":_("Settings"),
	"DESCRIPTION":_("Manage application"),
	"MENUDESCRIPTION":_("Configure some options"),
	"TOOLTIP":_("Set config level, default template.."),
	"USERCONF":_("The config will be applied per user"),
	"SYSCONF":_("The config will be applied to all users"),
	"N4DCONF":_("The config will be applied to all users and clients"),
	"LBLCONF":_("Choose the config level that should use the app"),
	"LBLSETTINGS":_("Session settings"),
	"LOADTPL":_("Load template on start"),
	"ENABLEDOCK":_("Enable accesshelper dock"),
	"AUTOSTART":_("Autostart enabled for user"),
	"DISABLEAUTOSTART":_("Autostart disabled for user"),
	"AUTOSTARTERROR":_("Autostart could not be disabled"),
	"ENABLEDOCK":_("Enabled accessibilty dock with hotkey"),
	"DISABLEDOCK":_("Disabled accessibilty dock"),
	"CONFIGLEVEL":_("Use config"),
	"PROFILE":_("Startup profile"),
	"NONE":_("Disabled"),
	"STARTDOCK":_("Autostart dock"),
	"DOCKHK":_("Hotkey for dock"),
	"GRUBBEEP":_("Beep when machine starts")
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
		self.accesshelper=libaccesshelper.accesshelper()
	#def __init__

	def _load_screen(self):
		def _change_osh():
			idx=self.cmb_level.currentIndex()
			if idx==0:
				lbl_help.setText(i18n.get("USERCONF"))
			elif idx==1:
				lbl_help.setText(i18n.get("SYSCONF"))
			elif idx==2:
				lbl_help.setText(i18n.get("N4DCONF"))
			self.fakeUpdate()
		self.installEventFilter(self)
		box=QGridLayout()
		lbl_txt=QLabel(i18n.get("LBLCONF"))
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
		box.addWidget(QLabel(i18n.get("LBLSETTINGS")),2,0,1,2,Qt.AlignTop)
		chk_template=QCheckBox(i18n.get("LOADTPL"))
		box.addWidget(chk_template,3,0,1,1,Qt.AlignTop)
		self.widgets.update({chk_template:'startup'})
		cmb_template=QComboBox()
		self.widgets.update({cmb_template:'profile'})
		box.addWidget(cmb_template,3,1,1,1,Qt.AlignTop)
		chk_dock=QCheckBox(i18n.get("ENABLEDOCK"))
		box.addWidget(chk_dock,4,0,1,1,Qt.AlignTop)
		self.widgets.update({chk_dock:'dock'})
		(mainHk,hkData,hkSetting,hkSection)=self.accesshelper.getHotkey("accessdock.desktop")
		if mainHk=="":
			mainHk="Ctrl+Space"
		self.btn_dockHk=appconfigControls.QHotkeyButton(mainHk)
		self.btn_dockHk.hotkeyAssigned.connect(self._testHotkey)
		box.addWidget(self.btn_dockHk,4,1,1,1,Qt.AlignTop)
		self.widgets.update({self.btn_dockHk:'dockHk'})
		chk_grub=QCheckBox(i18n.get("GRUBBEEP"))
		box.addWidget(chk_grub,5,0,1,1,Qt.AlignTop)
		self.widgets.update({chk_grub:'grubBeep'})
		box.setRowStretch(0,1)
		for i in range (1,5):
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
			elif desc=="grubBeep":
				if config[level].get("grubBeep","")=="true":
					widget.setChecked(True)
	#def _udpate_screen

	def _updateConfig(self,key):
		pass
	#def _updateConfig

	def _setAutostart(self,profile):
		if profile:
			cmd="/usr/share/accesshelper/accesshelp.py --set {}".format(profile)
			self.accesshelper.generateAutostartDesktop(cmd,self.profilerAuto)
			self.showMsg("{} {}".format(i18n.get("AUTOSTART"),os.environ.get("USER")))
	#def _setAutostart

	def _removeAutostart(self,profile):
		self.accesshelper.removeAutostartDesktop(self.profilerAuto)
		self.showMsg("{} {}".format(i18n.get("DISABLEAUTOSTART"),os.environ.get("USER")))
	#def _removeAutostart

	def _setAutostartDock(self):
		self.accesshelper.generateAutostartDesktop("/usr/share/accesshelper/accessdock.py","accessdock.desktop")
		btnHk="Ctrl+Space"
		for widget in self.widgets.keys():
			if isinstance(widget,appconfigControls.QHotkeyButton):
				btnHk=widget.text()
				break
		hotkey=btnHk
		desc="{0},{0},show accessdock".format(hotkey)
		data=[("_launch",desc),("_k_friendly_name","accessdock")]
		config={'kglobalshortcutsrc':{'accessdock.desktop':data}}
		self.accesshelper.setPlasmaConfig(config)
		self.showMsg("{0} {1}".format(i18n.get("ENABLEDOCK"),hotkey))

	def _removeAutostartDock(self):
		self.accesshelper.removeAutostartDesktop("accessdock.desktop")
		hotkey=""
		desc="{0},{0},show accessdock".format(hotkey)
		data=[("_launch",""),("_k_friendly_name","")]
		config={'kglobalshortcutsrc':{'accessdock.desktop':data}}
		self.accesshelper.setPlasmaConfig(config)
		self.showMsg("{}".format(i18n.get("DISABLEDOCK")))
	#def _removeAutostart

	def _setGrubBeep(self,value):
		self.accesshelper.setGrubBeep(value)
	#def _setGrubBeep

	def writeConfig(self):
		startWdg=None
		profile=''
		startdock=""
		startprofile=""
		dockhotkey=""
		configlevel=""
		config=self.getConfig()
		for widget,desc in self.widgets.items():
			if desc=="startup":
				startWdg=widget
			if desc=="dock":
				dockWdg=widget
			if desc=="dockHk":
				dockHk=widget
				dockhotkey=dockHk.text()
				if dockhotkey=="":
					dockhotkey="Ctrl+Space"
			if isinstance(widget,QCheckBox):
				value=widget.isChecked()
				if desc=="grubBeep":
					if config[self.level].get("grubBeep","")!=str(value).lower():
						self._setGrubBeep(value)
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
			startprofile=startWdg.isChecked()
			if startprofile:
				self._setAutostart(profile)
			else:
				self._removeAutostart(profile)
		if dockWdg:
			startdock=dockWdg.isChecked()
			if startdock: 
				self._setAutostartDock()
				self.saveChanges("dockHk",dockHk.text(),level="user")
			else:
				self._removeAutostartDock()
				self.saveChanges("dockHk","",level="user")
		self._writeFileChanges(configlevel,profile,startprofile,startdock,dockhotkey)
	#def writeConfig
		
	def _writeFileChanges(self,configlevel,profile,startprofile,startdock,dockhotkey):
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			f.write("{0}->{1}\n".format(i18n.get("CONFIGLEVEL"),configlevel))
			if startprofile:
				f.write("{0}->{1}\n".format(i18n.get("PROFILE"),profile))
			else:
				f.write("{0}->{1}\n".format(i18n.get("PROFILE"),i18n.get("NONE")))
			f.write("{0}->{1}\n".format(i18n.get("STARTDOCK"),i18n.get(str(startdock).upper())))
			f.write("{0}->{1}\n".format(i18n.get("DOCKHK"),dockhotkey))
	#def _writeFileChanges(self):
