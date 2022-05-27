#!/usr/bin/python3
from . import libaccesshelper
from . import libhotkeys
import os
from PySide2.QtWidgets import QApplication,QLabel,QGridLayout,QCheckBox,QSizePolicy,QRadioButton,QTableWidget,QHeaderView
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
		self.tblGrid.setColumnCount(2)
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
		for chk,btn in self.chkbtn.items():
			if isinstance(chk,QCheckBox):
				if chk.isChecked():
					if isinstance(btn,libhotkeys.QHotkeyButton):
						if btn.isVisible():
							btn.setEnabled(True)
				else:
					if isinstance(btn,libhotkeys.QHotkeyButton):
						if btn.isVisible():
							btn.setEnabled(False)

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
		#			settings=self.sortArraySettings(settings)
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
						chk.stateChanged.connect(self._updateButtons)
						self.tblGrid.setCellWidget(row,0,chk)
						(mainHk,hkData,hkSetting,hkSection)=self.accesshelper.getHotkey(name)
						if mainHk=="none":
							mainHk=""
						if mainHk=="":
							mainHk=name
						if name.upper() not in ["SYSTEMBELL","VISIBLEBELL","SNAPHELPERENABLED"]:
							btn=libhotkeys.QHotkeyButton(mainHk)
							btn.hotkeyAssigned.connect(self._testHotkey)
							self.chkbtn[chk]=btn
							self.tblGrid.setCellWidget(row,1,btn)
							btn.setEnabled(False)
						self.tblGrid.resizeRowToContents(row)
		chk=QCheckBox("{} (Meta+=/Meta+-)".format(i18n.get("MAGNIFIEREFFECTS")))
		chk.stateChanged.connect(self._setZoomOptionsEnabled)
		row=self.tblGrid.rowCount()
		self.tblGrid.setRowCount(row+1)
		self.tblGrid.setCellWidget(row,0,chk)
		self.tblGrid.resizeRowToContents(row)
		for setting in zoomOptions:
			row=self.tblGrid.rowCount()
			self.tblGrid.setRowCount(row+1)
			(name,data)=setting
			desc=i18n.get(name.upper(),name)
			btn=QRadioButton(desc)
			self.tblGrid.setCellWidget(row,1,btn)
		self._updateButtons()
		self._setZoomOptionsEnabled()
		return
	#def _update_screen

	def _setZoomOptionsEnabled(self):
		return
		if isinstance(self.widgets.get("magnifier",None),QCheckBox):
			state=self.widgets.get("magnifier").isChecked()
			for i in ["magnifierEnabled","zoomEnabled","lookingglassEnabled"]:
				if state==False:
					self.widgets.get(i).setChecked(False)
				self.widgets.get(i).setEnabled(state)
	#def _setZoomOptionsEnabled

	def _updateConfig(self,*args):
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		return
	#def _updateConfig

	def writeConfig(self):
		return
		plasmaConfig=self.plasmaConfig.copy()
		for kfile in self.wrkFiles:
			for section,data in plasmaConfig.get(kfile,{}).items():
				dataTmp=[]
				for setting,value in data:
					#btn=self.widgets.get(setting,'')
					btn=""
					if btn:
						if isinstance(btn,QCheckBox) or isinstance(btn,QRadioButton):
							#Optionbuttons depends on magnifier state
							value=""
							if isinstance(btn,QRadioButton):
								if self.widgets.get("magnifier").isChecked()==False:
									value="false"
							if value!="false":
								value=btn.isChecked()
								if value:
									value="true"
								else:
									value="false"
					dataTmp.append((setting,value))
				self.plasmaConfig[kfile][section]=dataTmp
		self.sysconfig=self._writeHotkeys()
		self.accesshelper.setPlasmaConfig(self.plasmaConfig)
		self.optionChanged=[]
		self._updateConfig()
		self.updateScreen()
		self.refresh=True
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		return

	def _writeHotkeys(self):
		return
		self.plasmaConfig["kglobalshortcutsrc"]={}
		for desc,widget in self.widgets.items():
			if isinstance(widget,libhotkeys.QHotkeyButton):
					desc=desc.replace("btn_","")
					if desc.upper() in actionHk.keys():
						(mainHk,hkData,hkSetting,hkSection)=self.accesshelper.getHotkey(actionHk[desc.upper()])
						newHk=widget.text()
						if newHk!=mainHk:
							hkData=hkData.split(",")
							hkData[0]=newHk
							if len(hkData)<=1:
								hkData.append(newHk)
								dataDesc=desc.upper()
								hkData.append(i18n.get(dataDesc,dataDesc))
								#hkSetting=descHk.get(desc,desc)  
								hkSection="kwin"
							else:
								hkData[1]=newHk
							hkSetting=actionHk.get(desc.upper())
							hkData=",".join(hkData)
						if self.plasmaConfig["kglobalshortcutsrc"].get(hkSection,None)==None:
							self.plasmaConfig["kglobalshortcutsrc"][hkSection]=[]
						self.plasmaConfig["kglobalshortcutsrc"][hkSection].append((hkSetting,hkData))
