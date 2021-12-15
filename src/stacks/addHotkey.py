#!/usr/bin/python3
from . import functionHelper
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QComboBox,QRadioButton,QListWidget,QGroupBox
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QSignalMapper,QProcess,QEvent,QSize
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import json
import subprocess
QString=type("")

i18n={
	"HOTKEYS":_("Keyboard Shortcuts"),
	"ACCESSIBILITY":_("hotkeys options"),
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Add hotkey"),
	"MENUDESCRIPTION":_("Add a hotkey for an application, command or action"),
	"TOOLTIP":_("Assign actions to keys"),
	"TYPEAPP":_("Application from system"),
	"TYPECMD":_("Command-line order"),
	"TYPEACT":_("Desktop action"),
	"LBLCMD":_("Command")
	}

class addHotkey(confStack):
	keybind_signal=Signal("PyObject")
	def __init_stack__(self):
		self.dbg=True
		self._debug("addhotkeys load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('input-keyboard')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=7
		self.visible=False
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.sysConfig={}
		self.wrkFiles=["kglobalshortcutsrc"]
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
	#def __init__

	def _load_screen(self):
		self.installEventFilter(self)
		self.box=QGridLayout()
		self.setLayout(self.box)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._grab_alt_keys)
		self.widgets={}
		self.widgetsText={}
		self.refresh=True
		grpOptions=QGroupBox()
		layOption=QGridLayout()
		opt=QRadioButton(i18n.get("TYPEAPP"))
		opt.toggled.connect(lambda: self.updateScreen(opt))
		self.widgets.update({opt:"TYPEAPP"})
		layOption.addWidget(opt,0,0)
		opt1=QRadioButton(i18n.get("TYPECMD"))
		opt1.toggled.connect(lambda: self.updateScreen(opt1))
		self.widgets.update({opt1:"TYPECMD"})
		layOption.addWidget(opt1,0,1)
		opt2=QRadioButton(i18n.get("TYPEACT"))
		opt2.toggled.connect(lambda: self.updateScreen(opt2))
		self.widgets.update({opt2:"TYPEACT"})
		layOption.addWidget(opt2,1,0)
		grpOptions.setLayout(layOption)
		self.box.addWidget(grpOptions,0,0,1,3)
		btn=QPushButton("")
		self.box.addWidget(btn,1,0,2,1)
		self.lstOptions=QListWidget()
		self.box.addWidget(self.lstOptions,1,1,1,2)
		lbl=QLabel(i18n.get("LBLCMD"))
		self.box.addWidget(lbl,2,1,1,1)
		self.inpCmd=QLineEdit()
		self.box.addWidget(self.inpCmd,2,2,1,1)
		opt.setChecked(True)
		#self.updateScreen()
	#def _load_screen

	def _addHotkey(self,*args):
		print(args)

	def _grab_alt_keys(self,*args):
		desc=''
		btn=''
		self.btn=btn
		if len(args)>0:
			desc=args[0]
		if desc:
			btn=self.widgets.get(desc,'')
		if btn:
			btn.setText("")
			self.grabKeyboard()
			self.keybind_signal.connect(self._set_config_key)
			self.btn=btn
	#def _grab_alt_keys

	def _set_config_key(self,keypress):
		keypress=keypress.replace("Control","Ctrl")
		self.btn.setText(keypress)
		desc=self.widgetsText.get(self.btn)
		sysConfig=self.sysConfig.copy()
		for kfile in self.wrkFiles:
			for section,data in sysConfig.get(kfile,{}).items():
				dataTmp=[]
				for setting,value in data:
					if setting==desc:
						valueArray=value.split(",")
						valueArray[0]=keypress
						valueArray[1]=keypress
						value=",".join(valueArray)
					dataTmp.append((setting,value))
				self.sysConfig[kfile][section]=dataTmp
		#if keypress!=self.keytext:
		#	self.changes=True
		#	self.setChanged(self.btn_conf)
	#def _set_config_key

	def eventFilter(self,source,event):
		sw_mod=False
		keypressed=[]
		if (event.type()==QEvent.KeyPress):
			for modifier,text in self.modmap.items():
				if event.modifiers() & modifier:
					sw_mod=True
					keypressed.append(text)
			key=self.keymap.get(event.key(),event.text())
			if key not in keypressed:
				if sw_mod==True:
					sw_mod=False
				keypressed.append(key)
			if sw_mod==False:
				self.keybind_signal.emit("+".join(keypressed))
		if (event.type()==QEvent.KeyRelease):
			self.releaseKeyboard()

		return False
	#def eventFilter

	def updateScreen(self,*args):
		if args:
			if isinstance(args[0],QRadioButton):
				if args[0].isChecked():
					desc=self.widgets.get(args[0])
					self.lstOptions.clear()
					if desc=="TYPEAPP":
						pass
					elif desc=="TYPECMD":
						self.inpCmd.enable()
						pass
					elif desc=="TYPEACT":
						pass

		
		pass
	#def _udpate_screen

	def _updateConfig(self,name):
		pass

	def writeConfig(self):
		#functionHelper.setSystemConfig(self.sysConfig)
		self.refresh=True
		self.optionChanged=[]
		self.stack.gotoStack(idx=4,parms="")
