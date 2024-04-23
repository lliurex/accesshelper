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
		self.text=QLabel("")
		lay=QGridLayout()
		self.icon=QtGui.QPixmap()
		lay.addWidget(self.text)
		self.installEventFilter(self)
		icon=QtGui.QIcon.fromTheme("edit-delete")
		self.setPixmap(icon.pixmap(48,48))
		self.setIconSize(QSize(48,48))
		self.row=row
	def setIconSize(self,*args):
		pass
	def setIcon(self,icon):
		self.setPixmap(icon.pixmap(48,48))
		self.setIconSize(QSize(48,48))
	def mousePressEvent(self, ev):
		self.clicked.emit(self)
#class delButton


i18n={
	"CONFIG":_("Hotkeys"),
	"HOTKEYS":_("Keyboard Shortcuts"),
	"ACCESSIBILITY":_("hotkeys options"),
	"DESCRIPTION":_("Keyboard Hotkeys"),
	"MENUDESCRIPTION":_("Set hotkeys for launch applications"),
	"TOOLTIP":_("From here you can set hotkeys for launch apps"),
	"NEXTWINDOW":_("Go to next window"),
	"PREVWINDOW":_("Go to previous window"),
	"CLOSEWINDOW":_("Close window"),
	"LAUNCHCOMMAND":_("Open launch menu"),
	"SHOWDESKTOP":_("Show desktop"),
	"Invert":_("Invert colours"),
	"InvertWindow":_("Invert window colours"),
	"ShowDesktopGrid":_("Show grid when moving windows"),
	"ToggleMouseClick":_("Show mouse click"),
	"view_zoom_in":_("Zoom in"),
	"view_zoom_out":_("Zoom out"),
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
		self.btn_add=QPushButton(_("Add new"))
		self.btn_add.clicked.connect(self._addHotkey)
		self.box.addWidget(self.btn_add,1,0,1,1)
	#def _load_screen

	def _getDescFromi18(self,i18desc):
		desc=i18desc	
		for key,item in i18n.items():
			if item.lower().strip()==i18desc.lower().strip():
				desc=key
				break
		return desc
	#def _getDescFromi18

	def _addHotkey(self,*args):
		cursor=QtGui.QCursor(Qt.WaitCursor)
		oldCursor=self.cursor()
		self.setCursor(cursor)
		self.stack.gotoStack(idx=9,parms=True)
		self.force_change=True
		self.setChanged(False)
		self.setCursor(oldCursor)
	#def _addHotkey

	def _deleteHotkey(self,btnDelete):
		#Check if deleting or undoing
		self.tblGrid.setCurrentCell(btnDelete.row,0)
		app=self.tblGrid.cellWidget(self.tblGrid.currentRow(),0)
		btn=self.tblGrid.cellWidget(self.tblGrid.currentRow(),1)
		if app.isEnabled():
			keypress=""
			self._debug("Delete event from {}".format(btnDelete))
			btn.setText("")
			app.setEnabled(False)
			icon=QtGui.QIcon.fromTheme("edit-undo")
			btnDelete.setIcon(icon)
			btn.setEnabled(False)
		else:
			self._undoDelete(app,btn)
			icon=QtGui.QIcon.fromTheme("edit-delete")
			btnDelete.setIcon(icon)
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
		#self._set_config_key(keypress)
	#def _deleteHotkey

	def _undoDelete(self,app,btn):
		for desktop,info in self.config.get('hotkeys',{}).items():
			name=desktop.replace("[","").replace("]","").replace(".desktop","")
			if app.text()==name:
				app.setEnabled(True)
				btn.setEnabled(True)
				hk=info.get("_launch","").split(",")[0]
				btn.setText(hk)
				break
	#def _undoDelete

	def updateScreen(self):
		self.tblGrid.clear()
		self.tblGrid.setRowCount(0)
		self._loadPlasmaHotkeys()
		self.lastKdeRow=self.tblGrid.rowCount()
		self._loadAccessHotkeys()
		self.tblGrid.resizeColumnToContents(1)
	#def _update_screen

	def setParms(self,*args):
		self.optionChanged=[]
		self.updateScreen()

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
					if len(data)>1 and desc==name:
						desc=data[-1]
					if (data[0].strip()=="" or data[0]=="none"):
						if name=="ShowDesktopGrid":
							data[0]="Ctrl+F8"
						elif name=="Invert":
							data[0]="Meta+Ctrl+I"
						elif name=="InvertWindow":
							data[0]="Meta+Ctrl+U"
						elif name=="TrackMouse":
							data[0]="Meta+/"
						elif name=="ToggleMouseClick":
							data[0]="Meta+*"

					lbl=QLabel(desc)
					btn=appconfigControls.QHotkeyButton(data[0])
					if data[0]=="none":
						btn.setText("")
					btn.hotkeyAssigned.connect(self._testHotkey)
					self.tblGrid.setCellWidget(row,0,lbl)
					self.tblGrid.setCellWidget(row,1,btn)
					self.tblGrid.resizeRowToContents(row)
	#def _loadPlasmaHotkeys

	def _loadAccessHotkeys(self):
		self.setChanged(True)
		self.config=self.getConfig().get(self.level)
		self.setChanged(False)
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

	def _updateHotkeysFromTable(self):
		plasmaConfig=self.plasmaConfig.copy()
		for i in range(self.tblGrid.rowCount()):
			desc=self.tblGrid.cellWidget(i,0).text()
			desc=self._getDescFromi18(desc)
			self._debug("Search for {} Row {} lastKdeRow {}".format(desc,i,self.lastKdeRow))
			hotkey=self.tblGrid.cellWidget(i,1).text()
			if i<self.lastKdeRow:
				self._getPlasmaHotkeysFromTable(desc,hotkey)
			else:
				self._debug("Config Value {} -> {}".format(desc,hotkey))
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
					arraySetting[1]="none"
					value=",".join(arraySetting)
				newSettings.append((description,value))
			if 'kwin' in sections.keys():
				newSections['kwin']=newSettings
				self.plasmaConfig.update({kfile:newSections})
	#def _getPlasmaHotkeysFromTable

	def _getConfigHotkeysFromTable(self,desc,hotkey):
		newHotkeys=self.config.get("hotkeys",{}).copy()
		if "[{}.desktop]".format(desc) in self.config.get('hotkeys',{}).keys() or len(self.config.get('hotkeys',{}))==0:
			#Don't delete if empty
			if len(hotkey)<=0 or str(hotkey).lower()=="none":
				value={'_launch':"",'_k_friendly_name':desc}
			else:
				friendly_name=newHotkeys.get("[{}.desktop]".format(desc),{}).get('_k_friendly_name',desc)
				value={'_launch':"{},none".format(hotkey),'_k_friendly_name':friendly_name}
			newHotkeys.update({"[{}.desktop]".format(desc):value})
		self.config.update({'hotkeys':newHotkeys})
	#def _getConfigHotkeysFromTable

	def writeConfig(self):
		#self.config=self.getConfig().get(self.level)
		self._updateHotkeysFromTable()
		self.accesshelper.setPlasmaConfig(self.plasmaConfig)
		hotkeys=self.config.get('hotkeys',{})
		for app,conf in hotkeys.items():
			hk=conf.get("_launch","").split(",")[0]
			desc=conf.get("_k_friendly_name",app)
			cmd=app.replace("[","")
			cmd=cmd.replace("]","")
			self._debug("HK {} for c:{} d:{}".format(hk,cmd,desc))
			self.accesshelper.setHotkey(hk,desc,cmd)
		dictHk=hotkeys.copy()
		for hk,data in hotkeys.items():
			if len(data.get("_launch",""))==0:
				dictHk.pop(hk)
		self.saveChanges('hotkeys',dictHk,'user')
		self.refresh=True
		self.optionChanged=[]
		self._writeFileChanges()
		self.updateScreen()
	#def writeConfig

	def _writeFileChanges(self):
		hotkeys=self.config.get('hotkeys',{})
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			for kfile,sections in self.plasmaConfig.items():
				for section,settings in sections.items():
					for setting in settings:
						arrayDesc=setting[1].split(",")
						f.write("{0}->{1}\n".format(i18n.get(arrayDesc[-1],arrayDesc[-1]),setting[1]))
			for key,launchable in hotkeys.items():
				friendly=launchable.get('_k_friendly_name',key)
				hotkey=launchable.get('_launch',"").split(",")
				f.write("{0}->{1}\n".format(friendly,hotkey[0]))

	#def _writeFileChanges(self):
