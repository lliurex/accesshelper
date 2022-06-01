#!/usr/bin/python3
from . import libaccesshelper
from appconfig import appconfigControls
import os
from PySide2.QtWidgets import QApplication, QLabel, QPushButton,QGridLayout,QTableWidget,QHeaderView
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QSize
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import json
import subprocess
QString=type("")

class delButton(QLabel):
	clicked=Signal("PyObject")
	def __init__(self,row=0,parent=None):
		QLabel.__init__(self, parent)
		self.installEventFilter(self)
		icon=QtGui.QIcon.fromTheme("edit-delete")
		self.setPixmap(icon.pixmap(48,48))
		self.setIconSize(QSize(48,48))
		self.row=row
	def setIconSize(self,*args):
		pass
	def mousePressEvent(self, ev):
		self.clicked.emit(self)


i18n={
	"CONFIG":_("Hotkeys"),
	"HOTKEYS":_("Keyboard Shortcuts"),
	"ACCESSIBILITY":_("hotkeys options"),
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
	"HKASSIGNED":_("already assigned to action")
	}

class assignHotkeys(confStack):
	def __init_stack__(self):
		self.dbg=False
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
		self.accesshelper=libaccesshelper.accesshelper()
		self.lastKdeRow=0
	#def __init__

	def _load_screen(self):
		self.installEventFilter(self)
		self.box=QGridLayout()
		self.tblGrid=QTableWidget(0,3)
		font=self.tblGrid.font()
		minsize=font.pointSize()
		self.setLayout(self.box)
		self.tblGrid.setShowGrid(False)
		self.tblGrid.verticalHeader().hide()
		self.tblGrid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.tblGrid.horizontalHeader().hide()
		self.tblGrid.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
		self.tblGrid.setSelectionBehavior(self.tblGrid.SelectRows)
		self.tblGrid.setSelectionMode(self.tblGrid.SingleSelection)
		self.box.addWidget(self.tblGrid,0,0,1,1)
		btn_add=QPushButton(_("Add new"))
		btn_add.clicked.connect(self._addHotkey)
		self.box.addWidget(btn_add,1,0,1,1)
		self._debug("LOAD SCREEN FINISHED")
		#self.updateScreen()
	#def _load_screen

	def _addHotkey(self,*args):
		self.stack.gotoStack(idx=9,parms="")

	def _deleteHotkey(self,btnDelete):
		keypress=""
		self.tblGrid.setCurrentCell(btnDelete.row,0)
		self._debug("Delete event from {}".format(btnDelete))
		btn=self.tblGrid.cellWidget(self.tblGrid.currentRow(),1)
		btn.setText("")
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
		#self._set_config_key(keypress)
	#def _deleteHotkey

	def updateScreen(self):
		self.tblGrid.clear()
		self.tblGrid.setRowCount(0)
		self._loadPlasmaHotkeys()
		self.lastKdeRow=self.tblGrid.rowCount()
		self._loadAccessHotkeys()
		self.tblGrid.resizeColumnToContents(1)
		self._debug("UPDATE SCREEN FINISHED")
	#def _update_screen

	def _loadPlasmaHotkeys(self):
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
			for kfile,sections in plasmaConfig.items():
				settings=sections.get('kwin',[])
				for setting in settings:
					row=self.tblGrid.rowCount()
					self.tblGrid.setRowCount(row+1) 
					(name,data)=setting
					data=data.split(",")
					desc=i18n.get(name,name)
					if len(data)>1:
						desc=data[-1]
					lbl=QLabel(desc)
					btn=appconfigControls.QHotkeyButton(data[0])
					btn.hotkeyAssigned.connect(self._testHotkey)
					self.tblGrid.setCellWidget(row,0,lbl)
					self.tblGrid.setCellWidget(row,1,btn)
					self.tblGrid.resizeRowToContents(row)
	#def _loadPlasmaHotkeys

	def _loadAccessHotkeys(self):
		self.changes=True #Forces data refresh
		self.config=self.getConfig().get(self.level)
		self.changes=False
		for desktop,info in self.config.get('hotkeys',{}).items():
			row=self.tblGrid.rowCount()
			self.tblGrid.setRowCount(row+1) 
			name=desktop.replace("[","").replace("]","").replace(".desktop","")
			hk=info.get("_launch","").split(",")[0]
			lbl=QLabel(name)
			btn=appconfigControls.QHotkeyButton(text=hk)
			btn.hotkeyAssigned.connect(self._testHotkey)
			btnDel=delButton(row)
			btnDel.clicked.connect(self._deleteHotkey)
			delName="{}_btn_delete".format(name)
			self.tblGrid.setCellWidget(row,0,lbl)
			self.tblGrid.setCellWidget(row,1,btn)
			self.tblGrid.setCellWidget(row,2,btnDel)
			self.tblGrid.resizeRowToContents(row)
	#def _loadAccessHotkeys

	def _testHotkey(self,hotkey):
		self._debug("Read Hotkey {} on row {}".format(hotkey,self.tblGrid.currentRow()))
		if not hotkey.get("action","")=="":
			try:
				self.showMsg("{0} {1} {2}".format(hotkey.get("hotkey"),i18n.get("HKASSIGNED"),hotkey.get("action")))
			except:
				pass
			btn=self.tblGrid.cellWidget(self.tblGrid.currentRow(),1)
			btn.revertHotkey()
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
	#def _testHotkey

	def _updateConfig(self,name):
		pass

	def _updateHotkeysFromTable(self):
		plasmaConfig=self.plasmaConfig.copy()
		for i in range(self.tblGrid.rowCount()):
			desc=self.tblGrid.cellWidget(i,0).text()
			self._debug("Search for {} Row {} lastKdeRow {}".format(desc,i,self.lastKdeRow))
			hotkey=self.tblGrid.cellWidget(i,1).text()
			if i<self.lastKdeRow:
				self._getPlasmaHotkeysFromTable(desc,hotkey)
			else:
				self._debug("Config Value")
				self._getConfigHotkeysFromTable(desc,hotkey)
	#def _updateHotkeysFromTable

	def _getPlasmaHotkeysFromTable(self,desc,hotkey):
		newSections={}
		for kfile,sections in self.plasmaConfig.items():
			settings=sections.get('kwin',[])
			newSettings=[]
			for setting in settings:
				(description,value)=setting
				if desc in value:
					arraySetting=value.split(',')
					arraySetting[0]=hotkey
					arraySetting[1]=hotkey
					value=",".join(arraySetting)
				newSettings.append((description,value))
			if 'kwin' in sections.keys():
				newSections['kwin']=newSettings
				self.plasmaConfig.update({kfile:newSections})
	#def _getPlasmaHotkeysFromTable

	def _getConfigHotkeysFromTable(self,desc,hotkey):
		newHotkeys={}
		add=True
		for app,value in self.config.get('hotkeys',{}).items():
			if app=="[{}.desktop]".format(desc):
				if hotkey=="":
					add=False
				else:
					hotkeyLine=value.get('_launch','')
					hotkeyArray=hotkeyLine.split(",")
					hotkeyArray[0]=hotkey
					hotkeyArray[1]=hotkey
					value.update({'_launch':",".join(hotkeyArray)})
			if add:
				newHotkeys.update({app:value})
		self.config.update({'hotkeys':newHotkeys})
	#def _getPlasmaHotkeysFromTable

	def writeConfig(self):
		self.changes=True #Forces data refresh
		self.config=self.getConfig().get(self.level)
		self.changes=False
		self._updateHotkeysFromTable()
		self.accesshelper.setPlasmaConfig(self.plasmaConfig)
		hotkeys=self.config.get('hotkeys',{})
		self.saveChanges('hotkeys',hotkeys,'user')
		self.refresh=True
		self.optionChanged=[]
		self._writeFileChanges()

	def _writeFileChanges(self):
		hotkeys=self.config.get('hotkeys',{})
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			for kfile,sections in self.plasmaConfig.items():
				for section,settings in sections.items():
					for setting in settings:
						arrayDesc=setting[1].split(",")
						f.write("{0}->{1}\n".format(arrayDesc[-1],setting[1]))
			for key,launchable in hotkeys.items():
				hotkey=launchable['_launch'].split(",")
				f.write("{0}->{1}\n".format(launchable['_k_friendly_name'],hotkey[0]))

	#def _writeFileChanges(self):
