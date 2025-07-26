#!/usr/bin/python3
from llxaccessibility import llxaccessibility
import os,shutil
import json
from PySide6.QtWidgets import QApplication,QLabel,QGridLayout,QCheckBox,QSizePolicy,QRadioButton,QHeaderView,QTableWidgetItem,QAbstractScrollArea,QTableWidget
from PySide6 import QtGui
from PySide6.QtCore import Qt,QThread,Signal
from QtExtraWidgets import QStackedWindowItem, QTableTouchWidget, QPushInfoButton
import subprocess
from rebost import store
import locale
import gettext
_ = gettext.gettext

i18n={
	"ACCE":_("System Accessibility"),
	"ACCEDSC":_("Plasma Accessibility module"),
	"ANTI":_("Joystick as mouse"),
	"ANTIDSC":_("Configure a gamepad/joystick as mouse"),
	"BROWS":_("Browsers accessibility"),
	"BROWSDSC":_("Selection of addons and configurations for accessible browsing"),
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
			appraw=json.loads(self.rebost.matchApp(app))
			bundle=""
			if len(appraw)>0:
				app=json.loads(appraw[0])
				for bun in app.get("bundle",{}).keys():
					if bun.lower()=="zomando":
						continue
					if self.rebost.getAppStatus(app.get("name"),bun)=="0":
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
					jInfo=json.loads(appInfo[0])
					self.icons.update({btn:jInfo.get("icon","default")})
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
			index=3,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.rebost=store.client()
		self.plasmaConfig={}
		self.hideControlButtons()
		self.locale=locale.getdefaultlocale()[0][0:2]
		self.launch=thLauncher()
		self.launch.finished.connect(self._endCmd)
	#def __init__

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.tblGrid=QTableTouchWidget()
		self.tblGrid.setColumnCount(3)
		self.tblGrid.verticalHeader().hide()
		self.tblGrid.horizontalHeader().hide()
		self.tblGrid.setSelectionBehavior(QTableWidget.SelectRows)
		self.tblGrid.setSelectionMode(QTableWidget.SingleSelection)
		self.tblGrid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.tblGrid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.box.addWidget(self.tblGrid)
		self._renderGui()
	#def __initScreen__

	def _renderGui(self):
		self.tblGrid.setRowCount(0)
		self.tblGrid.setRowCount(3)
		controls=[]
		btnAcce=QPushInfoButton()
		controls.append(btnAcce)
		btnAcce.setText(i18n.get("ACCE"))
		btnAcce.setDescription(i18n.get("ACCEDSC"))
		btnAcce.loadImg("preferences-desktop-accessibility")
		btnAcce.clicked.connect(self._launch)
		btnOrca=QPushInfoButton()
		controls.append(btnOrca)
		btnOrca.setText(i18n.get("ORCA"))
		btnOrca.setDescription(i18n.get("ORCADSC"))
		btnOrca.clicked.connect(self._launch)
		btnLtts=QPushInfoButton()
		controls.append(btnLtts)
		btnLtts.setText(i18n.get("LTTS"))
		btnLtts.setDescription(i18n.get("LTTSDSC"))
		fname=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","rsrc","ttsmanager.png")
		btnLtts.loadImg(fname)
		btnLtts.clicked.connect(self._launch)
		btnDock=QPushInfoButton()
		controls.append(btnDock)
		btnDock.setText(i18n.get("DOCK"))
		btnDock.setDescription(i18n.get("DOCKDSC"))
		dockIcn=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","dock","accessdock.png")
		btnDock.loadImg(dockIcn)
		btnDock.clicked.connect(self._launch)
		btnJoys=QPushInfoButton()
		controls.append(btnJoys)
		btnJoys.setText(i18n.get("ANTI"))
		btnJoys.setDescription(i18n.get("ANTIDSC"))
		btnJoys.clicked.connect(self._launch)
		btnEvia=QPushInfoButton()
		controls.append(btnEvia)
		btnEvia.setText(i18n.get("EVIA"))
		btnEvia.setDescription(i18n.get("EVIADSC"))
		btnEvia.clicked.connect(self._launch)
		btnBrows=QPushInfoButton()
		controls.append(btnBrows)
		btnBrows.setText(i18n.get("BROWS"))
		btnBrows.setDescription(i18n.get("BROWSDSC"))
		fname=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","rsrc","browsermanager.png")
		btnBrows.loadImg(fname)
		btnBrows.clicked.connect(self._launch)
		row,col=(0,0)
		for btn in controls:
			if row==self.tblGrid.rowCount():
				self.tblGrid.setRowCount(row+1)
			self.tblGrid.setCellWidget(row,col,btn)
			col+=1
			if col==3:
				col=0
				row+=1
		self.tblGrid.verticalHeader().setSectionResizeMode(self.tblGrid.rowCount()-1,QHeaderView.ResizeToContents)
		self.tblGrid.horizontalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)

		self.getInfoBtns=getAppsInfo([btnOrca,btnEvia,btnJoys])
		self.getInfoBtns.finished.connect(self._updateBtns)
		self.getInfoBtns.start()
	#def _renderGui

	def _updateBtns(self,*args,**kwargs):
		icons=args[0]
		for btn,icn in icons.items():
			size=btn.size()
			btn.loadImg(icn)
			btn.setMinimumSize(size)
	#def _updateBtns

	def _launch(self,*args):
		args[0].setEnabled(False)
		self.launch.setParms(args[0].text())
		self.launch.start()
	#def _launch

	def _endCmd(self,*args):
		for i in range(0,self.tblGrid.rowCount()):
			for j in range(0,self.tblGrid.columnCount()):
				wdg=self.tblGrid.cellWidget(i,j)
				if wdg!=None:
					if wdg.isEnabled()==False:
						wdg.setEnabled(True)
		
	#def _endCmd

	def updateScreen(self):
		pass
	#def updateScreen

