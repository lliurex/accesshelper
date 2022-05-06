#!/usr/bin/python3
from . import libaccesshelper
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
	"SHOWDESKTOP":_("Show desktop"),
	"Invert":_("Invert colours"),
	"InvertWindow":_("Invert window colours"),
	"ToggleMouseClick":_("Show mouse click"),
	"TrackMouse":_("Show mouse pointer"),
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
		self.plasmaConfig={}
		self.config={}
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
		self.accesshelper=libaccesshelper.accesshelper()
	#def __init__

	def _load_screen(self):
		self.installEventFilter(self)
		self.box=QGridLayout()
		self.tblGrid=QTableWidget(0,2)
		font=self.tblGrid.font()
		minsize=font.pointSize()
		self.setLayout(self.box)
		self.sigmap_run=QSignalMapper(self)
		self.sigmap_run.mapped[QString].connect(self._grab_alt_keys)
		config=self.getConfig().get(self.level)
		self.widgets={}
		self.widgetsText={}
		self.refresh=True
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
			for kfile,sections in plasmaConfig.items():
				settings=sections.get('kwin',[])
				row=0
				for setting in settings:
					self.tblGrid.setRowCount(row+1) 
					(name,data)=setting
					data=data.split(",")
					desc=i18n.get(name,name)
					if len(data)>1:
						desc=data[-1]
					lbl=QLabel(desc)
					#self.box.addWidget(lbl,row,0)
					self.tblGrid.setCellWidget(row,0,lbl)
					btn=QPushButton(data[0])
					self.sigmap_run.setMapping(btn,name)
					btn.clicked.connect(self.sigmap_run.map)
					self.tblGrid.setCellWidget(row,1,btn)
					self.tblGrid.resizeRowToContents(row)
					#self.box.addWidget(btn,row,1)
					row+=1
					self.widgets.update({name:btn})
					self.widgetsText.update({btn:name})

		for desktop,info in config.get('hotkeys',{}).items():
			self.tblGrid.setRowCount(row+1) 
			name=desktop.replace("[","").replace("]","").rstrip(".desktop")
			hk=info.get("_launch","").split(",")[0]
			lbl=QLabel(name)
			#self.box.addWidget(lbl,row,0)
			self.tblGrid.setCellWidget(row,0,lbl)
			btn=QPushButton(hk)
			self.sigmap_run.setMapping(btn,name)
			btn.clicked.connect(self.sigmap_run.map)
			#self.box.addWidget(btn,row,1)
			self.tblGrid.setCellWidget(row,1,btn)
			self.tblGrid.resizeRowToContents(row)
			row+=1
			self.widgets.update({name:btn})
			self.widgetsText.update({btn:name})
		self.tblGrid.setShowGrid(False)
		self.tblGrid.verticalHeader().hide()
		self.tblGrid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.tblGrid.horizontalHeader().hide()
		self.tblGrid.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
		self.tblGrid.resizeColumnToContents(1)
		self.tblGrid.setSelectionBehavior(self.tblGrid.SelectRows)
		self.tblGrid.setSelectionMode(self.tblGrid.SingleSelection)
		self.box.addWidget(self.tblGrid,0,0,1,1)


		btn_add=QPushButton(_("Add new"))
		btn_add.clicked.connect(self._addHotkey)
		self.box.addWidget(btn_add,row+1,0,1,1)
		self._debug("LOAD SCREEN FINISHED")
		#self.updateScreen()
	#def _load_screen

	def _addHotkey(self,*args):
		self.stack.gotoStack(idx=8,parms="")

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
		plasmaConfig=self.plasmaConfig.copy()
		for kfile in self.wrkFiles:
			for section,data in plasmaConfig.get(kfile,{}).items():
				dataTmp=[]
				for setting,value in data:
					if setting==desc:
						valueArray=value.split(",")
						valueArray[0]=keypress
						valueArray[1]=keypress
						valueArray[2]=valueArray[2].replace(",","")
						value=",".join(valueArray)
					dataTmp.append((setting,value))
				self.plasmaConfig[kfile][section]=dataTmp
		self.config=self.getConfig().get(self.level)
		config=self.config.copy()
		for setting,valueDict in config.get("hotkeys",{}).items():
			if isinstance(valueDict,dict):
				if valueDict.get('_launch','')!='':
					dataTmp=[]
					type(setting)
					valueArray=valueDict.get('_launch').split(",")
					desc=" ".join(valueArray[2:])
					value=",".join([keypress,keypress,desc])
					dataTmp.append(("_launch",value))
					self.config['hotkeys'][setting]["_launch"]=value
					k_friendly_name=setting.replace("[","").replace("]","").replace(".desktop","").capitalize()
					self.config['hotkeys'][setting]["_k_friendly_name"]=k_friendly_name
					dataTmp.append(("_k_friendly_name",k_friendly_name))
					self.plasmaConfig['kglobalshortcutsrc']["{}".format(setting.replace("[","").replace("]",""))]=dataTmp
			
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
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
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self._debug("Read {}".format(wrkFile))
			self.plasmaConfig.update(plasmaConfig)
			for kfile,sections in plasmaConfig.items():
				for section,settings in sections.items():
					self._debug("Section {}".format(section))
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
		self.changes=True
		config=self.getConfig().get(self.level)
		self.changes=False
		for desktop,info in config.get('hotkeys',{}).items():
			name=desktop.replace("[","").replace("]","").replace(".desktop","")
			btn=self.widgets.get(name,'')
			hk=info.get("_launch","").split(",")[0]
			if isinstance(btn,QPushButton):
				btn.setText(hk)
			else: #New button
				row=self.tblGrid.rowCount()
				self._debug("Add new button for {} at row".format(name,row))
				self.tblGrid.setRowCount(row+1) 
				lbl=QLabel(name)
				#self.box.addWidget(lbl,row,0)
				self.tblGrid.setCellWidget(row,0,lbl)
				btn=QPushButton(hk)
				self.sigmap_run.setMapping(btn,name)
				btn.clicked.connect(self.sigmap_run.map)
				#self.box.addWidget(btn,row,1)
				self.tblGrid.setCellWidget(row,1,btn)
				self.tblGrid.resizeRowToContents(row)
				btn.show()
				self.widgets.update({name:btn})
				self.widgetsText.update({btn:name})
		self._debug("UPDATE SCREEN FINISHED")
	#def _udpate_screen

	def _updateConfig(self,name):
		pass

	def writeConfig(self):
		self.accesshelper.setPlasmaConfig(self.plasmaConfig)
		self.saveChanges('hotkeys',self.config.get('hotkeys',{}),'user')
		self.refresh=True
		self.optionChanged=[]
		f=open("/tmp/accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		return
