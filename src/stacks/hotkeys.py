#!/usr/bin/python3
from . import functionHelper
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QComboBox,QCheckBox,QTableWidget,QHeaderView
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
	"DESCRIPTION":_("Hotkeys configuration"),
	"MENUDESCRIPTION":_("Set hotkeys for launch applications"),
	"TOOLTIP":_("From here you can set hotkeys for launch apps"),
	"NEXTWINDOW":_("Go to next window"),
	"PREVWINDOW":_("Go to previous window"),
	"CLOSEWINDOW":_("Close window"),
	"LAUNCHCOMMAND":_("Open launch menu"),
	"SHOWDESKTOP":_("Show desktop")
	}

class hotkeys(confStack):
	keybind_signal=Signal("PyObject")
	def __init_stack__(self):
		self.dbg=True
		self._debug("hotkeys load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('input-keyboard')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=4
		self.enabled=True
		self.changed=[]
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
		tblGrid=QTableWidget(0,2)
		font=tblGrid.font()
		minsize=font.pointSize()
		self.setLayout(self.box)
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._grab_alt_keys)
		config=self.getConfig().get(self.level)
		self.widgets={}
		self.widgetsText={}
		self.refresh=True
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile)
			self.sysConfig.update(systemConfig)
			for kfile,sections in systemConfig.items():
				for section,settings in sections.items():
					row=0
					for setting in settings:
						tblGrid.setRowCount(row+1) 
						(name,data)=setting
						data=data.split(",")
						desc=""
						if len(data)>0:
							desc=data[-1]
						lbl=QLabel(desc)
						#self.box.addWidget(lbl,row,0)
						tblGrid.setCellWidget(row,0,lbl)
						btn=QPushButton(data[0])
						sigmap_run.setMapping(btn,name)
						btn.clicked.connect(sigmap_run.map)
						tblGrid.setCellWidget(row,1,btn)
						tblGrid.resizeRowToContents(row)
						#self.box.addWidget(btn,row,1)
						row+=1
						self.widgets.update({name:btn})
						self.widgetsText.update({btn:name})

		for desktop,info in config.get('hotkeys',{}).items():
			tblGrid.setRowCount(row+1) 
			name=desktop.replace("[","").replace("]","").rstrip(".desktop")
			hk=info.get("_launch","").split(",")[0]
			lbl=QLabel(name)
			#self.box.addWidget(lbl,row,0)
			tblGrid.setCellWidget(row,0,lbl)
			btn=QPushButton(hk)
			sigmap_run.setMapping(btn,name)
			btn.clicked.connect(sigmap_run.map)
			#self.box.addWidget(btn,row,1)
			tblGrid.setCellWidget(row,1,btn)
			tblGrid.resizeRowToContents(row)
			row+=1
			self.widgets.update({name:btn})
			self.widgetsText.update({btn:name})
		tblGrid.setShowGrid(False)
		tblGrid.verticalHeader().hide()
		tblGrid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		tblGrid.horizontalHeader().hide()
		tblGrid.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
		tblGrid.resizeColumnToContents(1)
		tblGrid.setSelectionBehavior(tblGrid.SelectRows)
		tblGrid.setSelectionMode(tblGrid.SingleSelection)
		self.box.addWidget(tblGrid,0,0,1,1)


		btn_add=QPushButton(_("Add new"))
		btn_add.clicked.connect(self._addHotkey)
		self.box.addWidget(btn_add,row+1,0,1,1)
		self.updateScreen()
	#def _load_screen

	def _addHotkey(self,*args):
		self.stack.gotoStack(idx=17,parms="")

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

	def updateScreen(self):
		for wrkFile in self.wrkFiles:
			systemConfig=functionHelper.getSystemConfig(wrkFile)
			self.sysConfig.update(systemConfig)
			for kfile,sections in systemConfig.items():
				for section,settings in sections.items():
					row=0
					for setting in settings:
						(name,data)=setting
						data=data.split(",")
						desc=""
						if len(data)>0:
							desc=data[-1]
						btn=self.widgets.get(name)
						if btn:
							btn.setText(data[0])
							self.widgets.update({name:btn})
							self.widgetsText.update({btn:name})
		pass
	#def _udpate_screen

	def _updateConfig(self,name):
		pass

	def writeConfig(self):
		functionHelper.setSystemConfig(self.sysConfig)
		self.refresh=True
		self.optionChanged=[]
		f=open("/tmp/accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		return
