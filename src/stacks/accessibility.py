#!/usr/bin/python3
from llxaccessibility import llxaccessibility
import os,shutil
import json
from PySide6.QtWidgets import QApplication,QGridLayout,QListWidget,QListWidgetItem,QLabel
from PySide6 import QtGui
from PySide6.QtCore import Qt,QThread,Signal,QSize
from QtExtraWidgets import QStackedWindowItem, QPushInfoButton
import subprocess
from rebost import store
import gettext
_ = gettext.gettext

i18n={
	"ACCE":_("System Accessibility"),
	"ACCEDSC":_("Plasma Accessibility module"),
	"ANTI":_("Joystick as mouse"),
	"ANTIDSC":_("Configure a gamepad/joystick as mouse"),
	"BROW":_("Browsers accessibility"),
	"BROWDSC":_("Selection of addons and configurations for accessible browsing"),
	"CONFIG":_("Accessibility"),
	"DOCK":_("Accessibility Dock"),
	"DOCKDSC":_("Dock with customizable fast actions"),
	"EVIA":_("Webcam as mouse"),
	"EVIADSC":_("Webcam based mouse control"),
	"LTTS":_("LliureX TTS"),
	"LTTSDSC":_("Configure Lliurex TTS addon"),
	"MENU":_("Accessibility"),
	"ORCA":_("Orca"),
	"ORCADSC":_("Open Orca configuration tool"),
	"DESCRIPTION":_("Accesibility options"),
	"TOOLTIP":_("Settings which do the system more accessible"),
	}

class thLauncher(QThread):
	finished=Signal("PyObject")
	def __init__(self,parent=None,*args,**kwargs):
		super().__init__()
		self.accesshelper=llxaccessibility.client()
		self.rebost=store.client()
		self.cmd=""

	def setParms(self,*args):
		self.cmd=args[0]
	#def setParms

	def _getCmdArray(self,*args):
		cmd=args[0]
		procCmd=[]
		self.parms=[]
		if " " in cmd:
			procCmd.extend(cmd[0].split(" ")[1:])
			F
			procCmd.insert(0,cmd[0].split(" ")[0])
		else:
			if isinstance(cmd,str):
				procCmd=cmd.split(" ")
			else:
				procCmd=cmd
		self.cmd=procCmd[0]
		self.cmd.extend(cmd[1:])
	#def setParms

	def _getAppCmd(self,app):
		cmdPath=self._getPathForCmd(app)
		if len(cmdPath)>0:
			cmd=[cmdPath]
			if cmdPath.endswith("/orca"):
				cmd.append("-s")
		else:
			cmd=["/usr/bin/lliurex-store","appsedu://{}".format(app)]
			appraw=json.loads(self.rebost.showApp(app))
			bundle=""
			if len(appraw)>0:
				app=appraw[0]
				for bun in app.get("bundle",{}).keys():
					if bun.lower()=="unknown":
						continue
					if app.get("status",{}).get(bun,"1")=="0":
						bundle=bun
						break
				if bundle=="package":
					cmd=["gtk-launch",app.get("id",'')]
				elif bundle=="flatpak":
					cmd=["flatpak","run",app.get("bundle",{}).get("flatpak","")]
				elif bundle=="snap":
					cmd=["snap","run",app.get("bundle",{}).get("snap","")]
				elif bundle=="appimage":
					cmd=["gtk-launch","{}-appimage".format(app.get("pkgname",''))]
				#proc=subprocess.run(cmd)
		return(cmd)
	#def _getAppCmd

	def _getPathForCmd(self,cmd):
		cmdPath=None
		if os.path.isfile(cmd)==False:
			cmdPath=shutil.which(os.path.basename(cmd.split(" ")[0]))
		if cmdPath==None:
			cmdPath=""
		return(cmdPath)

	def run(self):
		if self.cmd==i18n.get("ACCE"):
			mod="kcm_access"
			self.cmd="kcm_access"
		else:
			if self.cmd==i18n.get("ORCA"):
				self.cmd=self._getAppCmd("orca")
			elif self.cmd==i18n.get("LTTS"):
				self.cmd=os.path.join(os.path.dirname(__file__),"..","tools","ttsmanager.py")
			elif self.cmd==i18n.get("DOCK"):
				self.cmd=os.path.join(os.path.dirname(__file__),"..","dock","accessdock-config.py")
			elif self.cmd==i18n.get("ANTI"):
				self.cmd=self._getAppCmd("antimicrox")
			elif self.cmd==i18n.get("EVIA"):
				self.cmd=self._getAppCmd("eviacam")
			elif self.cmd==i18n.get("BROWS"):
				self.cmd=os.path.join(os.path.dirname(__file__),"..","tools","browsermanager.py")
		print("{} -> {}".format(self.cmd,self.cmd))
		if "kcm" in self.cmd:
			proc=self.accesshelper.launchKcmModule(self.cmd)
		else:
			proc=self.accesshelper.launchCmd(self.cmd)
		self.finished.emit(proc)
	#def run
#class thLauncher

class getAppsInfo(QThread):
	finished=Signal("PyObject")
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.icons={}
		if len(args)>0:
			if isinstance(args[0],list):
				for btn in args[0]:
					self.icons[btn]=""
		self.rebost=store.client()

	def run(self):
		for btn in self.icons.keys():
			app=""
			if btn.text()==i18n.get("ORCA"):
				app="orca"	
			elif btn.text()==i18n.get("EVIA"):
				app="eviacam"
			elif btn.text()==i18n.get("ANTI"):
				app="antimicrox"
			if len(app)>0:
				appInfo=json.loads(self.rebost.showApp(app))
				if len(appInfo)>0:
					icn=appInfo[0].get("icon","default")
					icnName=os.path.basename(icn)
					cacheIcn=os.path.join("/home",os.getlogin(),".cache","rebost","imgs",icnName)
					if os.path.exists(cacheIcn):
						icn=cacheIcn
					self.icons.update({btn:icn})
		self.finished.emit(self.icons)
#class getAppInfo

class accessibility(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.setProps(shortDesc=i18n.get("MENU"),
			description=i18n.get('DESCRIPTION'),
			longDesc=i18n.get('DESCRIPTION'),
			icon="preferences-desktop-accessibility",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.rebost=store.client()
		self.plasmaConfig={}
		self.hideControlButtons()
		self.launch=thLauncher()
		self.launch.finished.connect(self._endCmd)
	#def __init__

	def __initScreen__(self):
		lay=QGridLayout()
		self.lstApps=QListWidget()
		lay.addWidget(self.lstApps)
		self.setLayout(lay)
		self._renderGui()
	#def __initScreen__

	def _endCmd(self,*args):
		for i in range(0,self.lstApps.count()):
			itm=self.lstApps.item(i)
			wdg=self.lstApps.itemWidget(itm)
			wdg.setEnabled(True)
	#def _endCmd

	def _launch(self,*args):
		args[0].setEnabled(False)
		self.launch.setParms(args[0].text())
		self.launch.start()
	#def _launch

	def _renderBtn(self,i18Text,i18Desc,img=""):
		btn=QPushInfoButton()
		btn.setText(i18n.get(i18Text))
		btn.setDescription(i18n.get(i18Desc))
		if img!="":
			btn.loadImg(img)
		btn.clicked.connect(self._launch)
		return(btn)
	#def _renderBtn

	def _updateBtns(self,*args,**kwargs):
		icons=args[0]
		for btn,icn in icons.items():
			size=btn.size()
			btn.loadImg(icn)
	#def _updateBtns

	def _renderGui(self):
		controls=[]
		btnAcce=self._renderBtn("ACCE","ACCEDSC","preferences-desktop-accessibility")
		controls.append(btnAcce)
		#self.box.addWidget(btnAcce,0,0,1,1)
		btnOrca=self._renderBtn("ORCA","ORCADSC","")
		controls.append(btnOrca)
		fname=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","rsrc","ttsmanager.png")
		btnLtts=self._renderBtn("LTTS","LTTSDSC",fname)
		controls.append(btnLtts)
		dockIcn=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","dock","accessdock.png")
		btnDock=self._renderBtn("DOCK","DOCKDSC",fname)
		controls.append(btnDock)
		btnJoys=self._renderBtn("ANTI","ANTIDSC","")
		controls.append(btnJoys)
		btnEvia=self._renderBtn("EVIA","EVIADSC","")
		controls.append(btnEvia)
		fname=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","rsrc","browsermanager.png")
		btnBrow=self._renderBtn("BROW","BROWDSC",fname)
		controls.append(btnBrow)
		for btn in controls:
			self.lstApps.addItem("")
			itm=self.lstApps.item(self.lstApps.count()-1)
			itm.setSizeHint(QSize(228,150))
			self.lstApps.setItemWidget(itm,btn)
		self.getInfoBtns=getAppsInfo([btnOrca,btnEvia,btnJoys])
		self.getInfoBtns.finished.connect(self._updateBtns)
		self.getInfoBtns.start()
	#def _renderGui

	def updateScreen(self):
		pass
	#def updateScreen

