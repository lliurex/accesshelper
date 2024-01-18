#!/usr/bin/python3
from . import libaccesshelper
#from appconfig import appconfigControls
import QtExtendedWidgets
import os
from PySide2.QtWidgets import QApplication,QLabel,QGridLayout,QCheckBox,QSizePolicy,QRadioButton,QHeaderView,QTableWidgetItem
from PySide2 import QtGui
from PySide2.QtCore import Qt
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext

i18n={
	"CONFIG":_("Accessibility"),
	"ACCESSIBILITY":_("Accessibility options"),
	"DESCRIPTION":_("Accessibility"),
	"MENUDESCRIPTION":_("Set accesibility options"),
	"TOOLTIP":_("From here you can activate/deactivate accessibility aids"),
	"INVERTENABLED":_("Invert screen colors"),
	"INVERTWINDOW":_("Invert windows colors"),
	"ANIMATEONCLICK":_("Show animation on click"),
	"SNAPHELPERENABLED":_("Show a grid when moving windows"),
	"LOOKINGGLASSENABLED":_("Activate eyefish effect"),
	"MAGNIFIERENABLED":_("Glass effect"),
	"ZOOMENABLED":_("Zoom effect"),
	"MAGNIFIEREFFECTS":_("Enable magnify effects"),
	"SYSTEMBELL":_("Acoustic system bell"),
	"VISIBLEBELL":_("Visible bell"),
	"TRACKMOUSEENABLED":_("Track pointer"),
	"HKASSIGNED":_("already assigned to action"),
	"MOUSECLICKENABLED":_("Track click"),
	"AUTOSTARTENABLED":_("Disable load profile on startup or changes will not apply on restart"),
	"FALSE":_("Disabled"),
	"TRUE":_("Enabled")
	}

descHk={
	"INVERTENABLED":_("Invert",),
	"INVERTWINDOW":_("InvertWindow"),
	"ANIMATEONCLICK":_("Show animation on click"),
	"SNAPHELPERENABLED":_("Show a grid when moving windows"),
	"LOOKINGGLASSENABLED":_("Activate eyefish effect"),
	"MAGNIFIERENABLED":_("Glass effect"),
	"ZOOMENABLED":_("Zoom effect"),
	"SYSTEMBELL":_("Acoustic system bell"),
	"VISIBLEBELL":_("Visible bell"),
	"TRACKMOUSEENABLED":_("TrackMouse"),
	"MOUSECLICKENABLED":_("ToggleMouseClick")
	}

actionHk={
	"INVERTENABLED":"Invert",
	"INVERTWINDOW":"InvertWindow",
	"TRACKMOUSEENABLED":"TrackMouse",
	"MOUSECLICKENABLED":"ToggleMouseClick",
	"SNAPHELPERENABLED":"ShowDesktopGrid"
	}
class access(confStack):
	def __init_stack__(self):
		self.dbg=False
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
		self.wrkFiles=["kaccessrc","kwinrc"]
		self.blockSettings={"kwinrc":["FocusPolicy"]}
		self.wantSettings={}
		self.optionChanged=[]
		self.chkbtn={}
		self.startup="false"
		self.zoomRow=0
		self.accesshelper=libaccesshelper.accesshelper()
		return(self)
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
	#def sortArraySettings(self,settings):

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.tblGrid=QtExtendedWidgets.QTableTouchWidget()
		self.tblGrid.setColumnCount(2)
		self.tblGrid.setShowGrid(False)
		self.tblGrid.verticalHeader().hide()
		self.tblGrid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.tblGrid.horizontalHeader().hide()
		self.tblGrid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.tblGrid.setSelectionBehavior(self.tblGrid.SelectRows)
		self.tblGrid.setSelectionMode(self.tblGrid.SingleSelection)
		self.box.addWidget(self.tblGrid)
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

	def _updateButtons(self,*args,inc=0):
		row=self.tblGrid.currentRow()+inc
		self._debug("Setting state for row {} {}".format(row,inc))
		btn=self.tblGrid.cellWidget(row,1)
		chk=self.tblGrid.cellWidget(row,0)
		newValue="false"
		if isinstance(chk,QCheckBox):
			newValue=str(chk.isChecked()).lower()
		elif isinstance(btn,QRadioButton):
			newValue=str(btn.isChecked()).lower()
		item=self.tblGrid.item(row,0)
		if item==None:
			return
		data=item.data(Qt.UserRole)
		(kfile,section,setting,value)=data.split("~")
		settings=self.plasmaConfig[kfile][section]
		if btn and chk:
			btn.setEnabled(chk.isChecked())
		elif btn: #disable all zoom options, enable it later
			settings=self._disableZoomOptions(settings)
			value="false"
		try:
			idx=settings.index((setting,value))
		except:
			idx=-1
		else:
			settings.pop(idx)
		settings.append((setting,newValue))
		itemData="{0}~{1}~{2}~{3}".format(kfile,section,setting,newValue)
		if btn and not chk:
			if newValue=="true":
				btn.setChecked(True)
		item.setData(Qt.UserRole,itemData)
		self.plasmaConfig[kfile][section]=settings
		self.btn_cancel.setEnabled(True)
		self.btn_ok.setEnabled(True)
		self.changes=True
	#def _updateButtons(self):

	def _disableZoomOptions(self,settings):
		for i in range(self.zoomRow+1,self.zoomRow+3):
			zbtn=self.tblGrid.cellWidget(i,1)
			zoomItem=self.tblGrid.item(i,0)
			zoomData=zoomItem.data(Qt.UserRole)
			(zkfile,zsection,zsetting,zvalue)=zoomData.split("~")
			idx=settings.index((zsetting,zvalue))
			settings.pop(idx)
			settings.append((zsetting,"false"))
			zoomItemData="{0}~{1}~{2}~{3}".format(zkfile,zsection,zsetting,"false")
			zoomItem.setData(Qt.UserRole,zoomItemData)
		return(settings)

	def updateScreen(self):
		self.tblGrid.clear()
		self.tblGrid.setRowCount(0)
		self.chkbtn={}
		self.refresh=True
		config=self.getConfig()
		self.startup=config.get(self.level,{}).get("startup","false")
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
			for kfile,sections in plasmaConfig.items():
				zoomOptions=[]
				zoomOptions.append(kfile)
				want=self.wantSettings.get(kfile,[])
				block=self.blockSettings.get(kfile,[])
				for section,settings in sections.items():
					zoomOptions.append(section)
					settings=self.sortArraySettings(settings)
					for setting in settings:
						(name,data)=setting
						if name in block or (len(want)>0 and name not in want):
							continue
						#if name.upper() in ["MAGNIFIERENABLED","ZOOMENABLED","LOOKINGGLASSENABLED"]:
						if name.upper() in ["MAGNIFIERENABLED","ZOOMENABLED"]:
							zoomOptions.append(setting)
							continue
						row=self.tblGrid.rowCount()
						self.tblGrid.setRowCount(row+1)
						desc=i18n.get(name.upper(),name)
						chk=QCheckBox(desc)
						if name.upper()=="SYSTEMBELL":
							if len(data)==0:
								data="true"
						if data=="true":
							chk.setChecked(True)
						chk.stateChanged.connect(self._updateButtons)
						self.tblGrid.setCellWidget(row,0,chk)
						item=QTableWidgetItem()
						itemData="{0}~{1}~{2}~{3}".format(kfile,section,name,data)
						item.setData(Qt.UserRole,itemData)
						self.tblGrid.setItem(row,0,item)
						if name.upper() not in ["SYSTEMBELL","VISIBLEBELL","SNAPHELPERENABLED"]:
							self._addHotkeyButton(name,row,chk)
						self.tblGrid.resizeRowToContents(row)
		self._loadZoomOptions(zoomOptions)
		self.btn_cancel.setEnabled(False)
		self.btn_ok.setEnabled(False)
	#def _update_screen

	def _addHotkeyButton(self,name,row,chk):
		(mainhk,hkdata,hksetting,hksection)=self.accesshelper.getHotkey(name)
		if (mainhk=="" or mainhk=="none"):
			if name=="invertenabled":
				mainhk="meta+ctrl+i"
			elif name=="invertwindow":
				mainhk="meta+ctrl+u"
			elif name=="trackmouseenabled":
				mainhk="meta+/"
			elif name=="mouseclickenabled":
				mainhk="meta+*"
		item=QTableWidgetItem()
		itemdata="{0}".format(hksetting)
		item.setData(Qt.UserRole,itemdata)
		self.tblGrid.setItem(row,1,item)
		btn=QtExtendedWidgets.QHotkeyButton()
		btn.setText(mainhk)
		btn.hotkeyAssigned.connect(self._testHotkey)
		self.chkbtn[chk]=btn
		self.tblGrid.setCellWidget(row,1,btn)
		btn.setEnabled(chk.isChecked())
	#def _addhotkeybutton

	def _loadZoomOptions(self,zoomOptions):
		chk=QCheckBox("{} (Meta+=/Meta+-)".format(i18n.get("MAGNIFIEREFFECTS")))
		chk.stateChanged.connect(self._setZoomOptionsEnabled)
		row=self.tblGrid.rowCount()
		self.tblGrid.setRowCount(row+1)
		self.tblGrid.setCellWidget(row,0,chk)
		self.zoomRow=row
		kfile=zoomOptions.pop(0)
		section=zoomOptions.pop(0)
		for setting in zoomOptions:
			row=self.tblGrid.rowCount()
			self.tblGrid.setRowCount(row+1)
			if isinstance(setting,tuple)==False:
				continue
			(name,data)=setting
			desc=i18n.get(name.upper(),name)
			btn=QRadioButton(desc)
			btn.toggled.connect(self._updateButtons)
			if data=="true":
				chk.setChecked(True)
				btn.setChecked(True)
			self.tblGrid.setCellWidget(row,1,btn)
			item=QTableWidgetItem()
			itemData="{0}~{1}~{2}~{3}".format(kfile,section,name,data)
			item.setData(Qt.UserRole,itemData)
			self.tblGrid.setItem(row,0,item)
			self.tblGrid.resizeRowToContents(row)
		self._setZoomOptionsEnabled()
	#def _loadZoomOptions

	def _setZoomOptionsEnabled(self,*args):
		chk=self.tblGrid.cellWidget(self.zoomRow,0)
		item=None
		anychk=False
		for i in range(self.zoomRow+1,self.zoomRow+4):
			opt=self.tblGrid.cellWidget(i,1)
			if item==None:
				item=self.tblGrid.item(i,0)
				if item:
					(kfile,section,setting,data)=item.data(Qt.UserRole).split("~")
					settings=self.plasmaConfig[kfile][section]
			if opt:
				if chk.isChecked()==False:
					self._disableZoomOptions(settings)
				if opt.isChecked()==True:# and opt.isEnabled():
					anychk=True
				opt.setEnabled(chk.isChecked())
		if (anychk==False) and (chk.isChecked()==True) and opt!=None:
			opt=self.tblGrid.cellWidget(self.zoomRow+1,1)
			opt.setChecked(True)
			row=self.tblGrid.rowCount()
			self._updateButtons(inc=1)
		self.btn_cancel.setEnabled(True)
		self.btn_ok.setEnabled(True)
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
				btn=self.tblGrid.cellWidget(i,1)
				if isinstance(btn,QtExtendedWidgets.QHotkeyButton):
					if (chk.isChecked()):
						hotkey=btn.text()
					else:
						hotkey=""
					item=self.tblGrid.item(i,1)
					setting=item.data(Qt.UserRole)
					self._setPlasmaHotkeysFromTable(setting,hotkey)
			else:
				btn=self.tblGrid.cellWidget(i,1)
				if isinstance(btn,QRadioButton):
					if btn.isChecked():
						pass
	#def updateHotkeysFromTable

	def _setPlasmaHotkeysFromTable(self,desc,hotkey):
		self._debug("Set hotkey {} for {}".format(hotkey,desc))
		newSettings=[]
		if self.plasmaConfig.get('kglobalshortcutsrc',{})=={}:
			self.plasmaConfig["kglobalshortcutsrc"]=self.accesshelper.getPlasmaConfig('kglobalshortcutsrc').get("kglobalshortcutsrc","")
		settings=self.plasmaConfig.get('kglobalshortcutsrc',{}).get("kwin",[])
		if len(settings)>0:
			for setting in settings:
				(description,value)=setting
				if description==desc:
					value="{0},{0},{1}".format(hotkey,desc)
				newSettings.append((description,value))
		self.plasmaConfig["kglobalshortcutsrc"]["kwin"]=newSettings
	#def _getPlasmaHotkeysFromTable

	def writeConfig(self):
		if self.startup=="true":
			self.showMsg(i18n.get("AUTOSTARTENABLED"))
		self.updateDataFromTable()
		#InvertWindow needso InvertScreen enabled
		plugins=self.plasmaConfig.get("kwinrc",{}).get("Plugins",[])
		newList={}
		swChange=False
		for plugin in plugins:
			newList[plugin[0]]=plugin[1]
		if newList.get("invertWindow","false")=="true" and newList["invertEnabled"]!="true":
			newList["invertEnabled"]="true"
			swChange=True
		if swChange:
			plugins=[]
			for key,item in newList.items():
				plugins.append((key,item))
			self.plasmaConfig["kwinrc"]["Plugins"]=plugins

		self.accesshelper.setPlasmaConfig(self.plasmaConfig)
		self.optionChanged=[]
		self.refresh=True
		self._writeFileChanges()
		return

	def _writeFileChanges(self):
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			for kfile,sections in self.plasmaConfig.items():
				for section,settings in sections.items():
					for setting in settings:
						if setting[1]!="":
							value=i18n.get(setting[1].upper(),i18n.get("FALSE"))
						else:
							value=i18n.get("FALSE")
						desc=i18n.get(setting[0].upper(),"")
						if desc!="":
							f.write("{0}->{1}\n".format(desc,value))
	#def _writeFileChanges(self):
