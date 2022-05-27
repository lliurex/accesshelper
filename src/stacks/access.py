#!/usr/bin/python3
from . import libaccesshelper
from . import libhotkeys
import os
from PySide2.QtWidgets import QApplication,QLabel,QGridLayout,QCheckBox,QSizePolicy,QRadioButton,QTableWidget,QHeaderView,QTableWidgetItem
from PySide2 import QtGui
from PySide2.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext

i18n={
	"COLOURS":_("Colours"),
	"FONTS":_("Fonts"),
	"CURSOR":_("Cursor"),
	"AIDS":_("Visual Aids"),
	"SCREEN":_("Screen Options"),
	"HOTKEYS":_("Keyboard Shortcuts"),
	"ACCESSIBILITY":_("Accessibility options"),
	"CONFIG":_("Configuration"),
	"DESCRIPTION":_("Accessibility configuration"),
	"MENUDESCRIPTION":_("Set accesibility options"),
	"TOOLTIP":_("From here you can activate/deactivate accessibility aids"),
	"HIGHCONTRAST":_("Enable high contrast palette"),
	"INVERTENABLED":_("Invert screen colors"),
	"INVERTWINDOW":_("Invert windows colors"),
	"ANIMATEONCLICK":_("Show animation on click"),
	"SNAPHELPERENABLED":_("Show a grid when moving windows"),
	"LOOKINGGLASSENABLED":_("Activate eyefish effect"),
	"MAGNIFIERENABLED":_("Glass effect"),
	"ZOOMENABLED":_("Zoom effect"),
	"MAGNIFIEREFFECTS":_("Enable magnify effects"),
	"SYSTEMBELL":_("Acoustic system bell"),
	"FOCUSPOLICY":_("Set the policy focus"),
	"VISIBLEBELL":_("Visible bell"),
	"TRACKMOUSEENABLED":_("Track pointer"),
	"HKASSIGNED":_("already assigned to action"),
	"MOUSECLICKENABLED":_("Track click")
	}
descHk={
	"INVERTENABLED":"Invert",
	"INVERTWINDOW":_("InvertWindow"),
	"ANIMATEONCLICK":_("Show animation on click"),
	"SNAPHELPERENABLED":_("Show a grid when moving windows"),
	"LOOKINGGLASSENABLED":_("Activate eyefish effect"),
	"MAGNIFIERENABLED":_("Glass effect"),
	"ZOOMENABLED":_("Zoom effect"),
	"SYSTEMBELL":_("Acoustic system bell"),
	"FOCUSPOLICY":_("Set the policy focus"),
	"VISIBLEBELL":_("Visible bell"),
	"TRACKMOUSEENABLED":_("TrackMouse"),
	"MOUSECLICKENABLED":_("ToggleMouseClick")
	}

actionHk={
	"INVERTENABLED":"Invert",
	"INVERTWINDOW":"InvertWindow",
	"TRACKMOUSEENABLED":"TrackMouse",
	"MOUSECLICKENABLED":"ToggleMouseClick"
	}
class access(confStack):
	def __init_stack__(self):
		self.dbg=True
		self._debug("access Load")
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-accessibility')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=1
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.config={}
		self.plasmaConfig={}
		self.wrkFiles=["kaccesrc","kwinrc"]
		self.blockSettings={"kwinrc":["FocusPolicy"]}
		self.wantSettings={}
		self.optionChanged=[]
		self.chkbtn={}
		self.accesshelper=libaccesshelper.accesshelper()
	#def __init__

	def sortArraySettings(self,settings):
		ordArray=[]
		ordDict={}
		for name,value in settings:
			if "bell" in name.lower():
				bell=ordDict.get('bell',[])
				bell.append((name,value))
				ordDict['bell']=bell
			elif "mouse" in name.lower():
				mouse=ordDict.get('mouse',[])
				mouse.append((name,value))
				ordDict['mouse']=mouse
			else:
				other=ordDict.get('other',[])
				other.append((name,value))
				ordDict['other']=other
		for key,item in ordDict.items():
			ordArray.extend(item)
			
		return(ordArray)

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.tblGrid=QTableWidget()
		self.tblGrid.setColumnCount(3)
		self.tblGrid.setShowGrid(False)
		self.tblGrid.verticalHeader().hide()
		self.tblGrid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.tblGrid.horizontalHeader().hide()
		self.tblGrid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.tblGrid.setSelectionBehavior(self.tblGrid.SelectRows)
		self.tblGrid.setSelectionMode(self.tblGrid.SingleSelection)
		self.box.addWidget(self.tblGrid)
		self.refresh=True
	#def _load_screen

	def _testHotkey(self,hotkey):
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

	def _updateButtons(self):
		row=self.tblGrid.currentRow()
		self._debug("Setting state for row {}".format(row))
		btn=self.tblGrid.cellWidget(row,1)
		chk=self.tblGrid.cellWidget(row,0)
		if btn:
			btn.setEnabled(chk.isChecked())
		self.btn_cancel.setEnabled(True)
		self.btn_ok.setEnabled(True)
	#def _updateButtons(self):

	def updateScreen(self):
		self.tblGrid.clear()
		self.tblGrid.setRowCount(0)
		self.chkbtn={}
		zoomOptions=[]
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
			for kfile,sections in plasmaConfig.items():
				want=self.wantSettings.get(kfile,[])
				block=self.blockSettings.get(kfile,[])
				for section,settings in sections.items():
					settings=self.sortArraySettings(settings)
					for setting in settings:
						(name,data)=setting
						if name in block or (len(want)>0 and name not in want):
							continue
						if name.upper() in ["MAGNIFIERENABLED","ZOOMENABLED","LOOKINGGLASSENABLED"]:
							zoomOptions.append(setting)
							continue
						row=self.tblGrid.rowCount()
						self.tblGrid.setRowCount(row+1)
						desc=i18n.get(name.upper(),name)
						chk=QCheckBox(desc)
						if data=="true":
							chk.setChecked(True)
						chk.stateChanged.connect(self._updateButtons)
						self.tblGrid.setCellWidget(row,0,chk)
						item=QTableWidgetItem()
						item.setData(Qt.UserRole,actionHk.get(name.upper(),name))
						self.tblGrid.setItem(row,2,item)
						if name.upper() not in ["SYSTEMBELL","VISIBLEBELL","SNAPHELPERENABLED"]:
							(mainHk,hkData,hkSetting,hkSection)=self.accesshelper.getHotkey(name)
							btn=libhotkeys.QHotkeyButton()
							btn.setText(mainHk)
							btn.hotkeyAssigned.connect(self._testHotkey)
							self.chkbtn[chk]=btn
							self.tblGrid.setCellWidget(row,1,btn)
							btn.setEnabled(chk.isChecked())
						self.tblGrid.resizeRowToContents(row)
		self._loadZoomOptions(zoomOptions)
	#def _update_screen

	def _loadZoomOptions(self,zoomOptions):
		chk=QCheckBox("{} (Meta+=/Meta+-)".format(i18n.get("MAGNIFIEREFFECTS")))
		chk.stateChanged.connect(self._setZoomOptionsEnabled)
		row=self.tblGrid.rowCount()
		self.tblGrid.setRowCount(row+1)
		self.tblGrid.setCellWidget(row,0,chk)
		zoomRow=row
		self.tblGrid.resizeRowToContents(row)
		for setting in zoomOptions:
			row=self.tblGrid.rowCount()
			self.tblGrid.setRowCount(row+1)
			(name,data)=setting
			desc=i18n.get(name.upper(),name)
			btn=QRadioButton(desc)
			self.tblGrid.setCellWidget(row,1,btn)
			item=QTableWidgetItem()
			item.setData(Qt.UserRole,name)
			self.tblGrid.setItem(row,2,item)
		self._setZoomOptionsEnabled(init=zoomRow)
	#def _loadZoomOptions

	def _setZoomOptionsEnabled(self,*args,init=None):
		if init:
			row=init
		else:
			row=self.tblGrid.currentRow()
		chk=self.tblGrid.cellWidget(row,0)
		for i in range(row+1,row+4):
			opt=self.tblGrid.cellWidget(i,1)
			if opt:
				opt.setEnabled(chk.isChecked())
	#def _setZoomOptionsEnabled

	def _updateConfig(self,*args):
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		return
	#def _updateConfig

	def updateDataFromTable(self):
		for i in range(self.tblGrid.rowCount()):
			chk=self.tblGrid.cellWidget(i,0)
			if chk:
				state=chk.isChecked()
			item=self.tblGrid.item(i,2)
			if item:
				value=item.data(Qt.UserRole)
			btn=self.tblGrid.cellWidget(i,1)
			hotkey=None
			if isinstance(btn,libhotkeys.QHotkeyButton):
				hotkey=btn.text()
				self._getPlasmaHotkeysFromTable(value,hotkey)
			elif isinstance(btn,QRadioButton):
				state=btn.isChecked()
			if isinstance(state,bool) and item:
				self._setPlasmaConfigFromTable(value,state)
	#def updateHotkeysFromTable

	def _getPlasmaHotkeysFromTable(self,desc,hotkey):
		self._debug("Set hotkey {} for {}".format(hotkey,desc))
		newSections={}
		plasmaConfig={}
		if self.plasmaConfig.get('kglobalshortcutsrc',{})=={}:
			plasmaConfig=self.accesshelper.getPlasmaConfig('kglobalshortcutsrc')
		else:
			plasmaConfig['kglobalshortcutsrc']=self.plasmaConfig.get('kglobalshortcutsrc')
		for kfile,sections in plasmaConfig.items():
			settings=sections.get('kwin',[])
			newSettings=[]
			for setting in settings:
				(description,value)=setting
				if description==desc:
					arraySetting=value.split(',')
					arraySetting[0]=hotkey
					arraySetting[1]=hotkey
					value=",".join(arraySetting)
				newSettings.append((description,value))
			if 'kwin' in sections.keys():
				newSections['kwin']=newSettings
				self.plasmaConfig.update({kfile:newSections})
	#def _getPlasmaHotkeysFromTable

	def _setPlasmaConfigFromTable(self,value,state):
		for kfile,sections in self.plasmaConfig.items():
			if kfile=='kglobalshortcutsrc':
				continue
			newSections={}
			for section,settings in sections.items():
				newSettings=[]
				for setting in settings:
					(description,origState)=setting
					if description==value:
						setting=(description,str(state).lower())
					newSettings.append(setting)
				newSections[section]=newSettings
			self.plasmaConfig.update({kfile:newSections})
	#def _setPlasmaConfigFromTable(self,value,state):

	def writeConfig(self):
		self.updateDataFromTable()
		self.accesshelper.setPlasmaConfig(self.plasmaConfig)
		self.optionChanged=[]
		self.refresh=True
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		return
