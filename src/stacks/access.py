#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QLineEdit,QHBoxLayout,QComboBox,QCheckBox,QListWidget,QSizePolicy,QRadioButton
from PySide2 import QtGui
from PySide2.QtCore import Qt,Signal,QSignalMapper,QEvent
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
import json
import subprocess
import dbus,dbus.service,dbus.exceptions
from . import libaccesshelper
_ = gettext.gettext
QString=type("")

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
	"SYSTEMBELL":_("Acoustic system bell"),
	"FOCUSPOLICY":_("Set the policy focus"),
	"VISIBLEBELL":_("Visible bell"),
	"TRACKMOUSEENABLED":_("Track pointer"),
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
	keybind_signal=Signal("PyObject")
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
		self.wrkFiles=["kaccesrc","kwinrc"]
		self.blockSettings={"kwinrc":["FocusPolicy","lookingglassEnabled"]}
		self.wantSettings={}
		self.widgets={}
		self.widgetsText={}
		self.optionChanged=[]
		self.keymap={}
		self.chkbtn={}
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
		def sortArraySettings(settings):
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
		self.installEventFilter(self)
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.refresh=True
		row,col=(0,0)
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
			for kfile,sections in plasmaConfig.items():
				want=self.wantSettings.get(kfile,[])
				block=self.blockSettings.get(kfile,[])
				for section,settings in sections.items():
					zoomOptions=[]
					settings=sortArraySettings(settings)

					for setting in settings:
						(name,data)=setting
						if name in block or (len(want)>0 and name not in want):
							continue
						if name.upper() in ["MAGNIFIERENABLED","ZOOMENABLED"]:
							zoomOptions.append(setting)
							continue
						desc=i18n.get(name.upper(),name)
						chk=QCheckBox(desc)
						chk.stateChanged.connect(self._updateButtons)
						self.widgets.update({name:chk})
						self.box.addWidget(chk,row,col)
						col+=1
						(mainHk,hkData,hkSetting,hkSection)=self.accesshelper.getHotkey(name)
						if mainHk=="none":
							mainHk=""
						btn=QPushButton(mainHk)
						name="btn_{}".format(name)
						if mainHk=="":
							mainHk=name
						self.widgets.update({name:btn})
						self.widgetsText.update({btn:{'mainHk':mainHk,'hkData':hkData,'hkSetting':hkSetting,'hkSection':hkSection}})
						self.box.addWidget(btn,row,col,Qt.Alignment(1))
						btn.setEnabled(False)
						col+=1
						if col==2:
							row+=1
							col=0
						if name.replace("btn_","").upper() not in ["SYSTEMBELL","VISIBLEBELL","SNAPHELPERENABLED"]:
							self.chkbtn[chk]=btn
						else:
							btn.hide()
					lbl=None
					for setting in zoomOptions:
						if lbl==None:
							lbl=QLabel("Meta+=/Meta+-")
							self.box.addWidget(lbl,row,1,2,1)
						(name,data)=setting
						desc=i18n.get(name.upper(),name)
						btn=QRadioButton(desc)
						self.widgets.update({name:btn})
						self.box.addWidget(btn,row,0)
						row+=1
		self.updateScreen()
	#def _load_screen

	def _updateButtons(self):
		for chk,btn in self.chkbtn.items():
			if isinstance(chk,QCheckBox):
				if chk.isChecked():
					if isinstance(btn,QPushButton):
						if btn.isVisible():
							btn.setEnabled(True)
				else:
					if isinstance(btn,QPushButton):
						if btn.isVisible():
							btn.setEnabled(False)

	def _grab_alt_keys(self,*args):
		desc=''
		btn=''
		self.btn=btn
		if len(args)>0:
			desc=args[0]
		if desc:
			btn=self.widgets.get(desc,'')
		if btn:
			btn.setText("Press keys")
			self.grabKeyboard()
			self.keybind_signal.connect(self._set_config_key)
			self.btn=btn
	#def _grab_alt_keys

	def _set_config_key(self,keypress):
		keypress=keypress.replace("Control","Ctrl")
		self.btn.setText(keypress)
		desc=self.widgetsText.get(self.btn).get("mainHk")
		plasmaConfig=self.plasmaConfig.copy()
		for kfile in self.wrkFiles:
			for section,data in plasmaConfig.get(kfile,{}).items():
				dataTmp=[]
				for setting,value in data:
					if setting==desc:
						valueArray=value.split(",")
						valueArray[0]=keypress
						valueArray[1]=keypress
						value=",".join(valueArray)
					dataTmp.append((setting,value))
				self.plasmaConfig[kfile][section]=dataTmp
		#if keypress!=self.keytext:
		#	self.changes=True
		#	self.setChanged(self.btn_conf)
		self.btn_ok.setEnabled(True)
		self.btn_cancel.setEnabled(True)
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
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._grab_alt_keys)
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		for kfile,sections in self.plasmaConfig.items():
			want=self.wantSettings.get(kfile,[])
			block=self.blockSettings.get(kfile,[])
			for section,settings in sections.items():
				zoomOptions=[]
				for setting in settings:
					(name,data)=setting
					if name in block or (len(want)>0 and name not in want):
						continue
					if (data.lower() in ("true","false")) or (data==''):
						state=False
						if data.lower()=="true":
							state=True
						if name:
							self.widgets.get(name).setChecked(state)

					(mainHk,hkData,hkSetting,hkSection)=self.accesshelper.getHotkey(name)

					if mainHk=="" or mainHk.lower()=="none":
						mainHk=""
					name="btn_{}".format(name)
					btn=self.widgets.get(name)
					if isinstance(btn,QPushButton):
						if btn.isVisible():
							btn.show()
							sigmap_run.setMapping(btn,name)
							self.widgets.update({name:btn})
							self.widgetsText.update({btn:{'mainHk':mainHk,'hkData':hkData,'hkSetting':hkSetting,'hkSection':hkSection}})
							btn.clicked.connect(sigmap_run.map)
							btn.setText(mainHk)
		self._updateButtons()
		return
	#def _udpate_screen

	def _updateConfig(self,*args):
		for wrkFile in self.wrkFiles:
			plasmaConfig=self.accesshelper.getPlasmaConfig(wrkFile)
			self.plasmaConfig.update(plasmaConfig)
		return
	#def _updateConfig

	def writeConfig(self):
		plasmaConfig=self.plasmaConfig.copy()
		for kfile in self.wrkFiles:
			for section,data in plasmaConfig.get(kfile,{}).items():
				dataTmp=[]
				for setting,value in data:
					btn=self.widgets.get(setting,'')
					if btn:
						if isinstance(btn,QCheckBox) or isinstance(btn,QRadioButton):
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
		self.plasmaConfig["kglobalshortcutsrc"]={}
		for desc,widget in self.widgets.items():
			if isinstance(widget,QPushButton):
					desc=desc.replace("btn_","")
					if desc.upper() in actionHk.keys():
						(mainHk,hkData,hkSetting,hkSection)=self.accesshelper.getHotkey(actionHk[desc.upper()])
						self._debug("*******************************")
						self._debug("mainHk: {}".format(mainHk))
						self._debug("hkData: {}".format(hkData))
						self._debug("hkSetting: {}".format(hkSetting))
						self._debug("hkSection: {}".format(hkSection))
						self._debug("*******************************")
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
