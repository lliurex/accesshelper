#!/usr/bin/python3
from llxaccessibility import llxaccessibility
import os,shutil
import json
from PySide2.QtWidgets import QApplication,QLabel,QGridLayout,QCheckBox,QSizePolicy,QRadioButton,QHeaderView,QTableWidgetItem,QAbstractScrollArea,QTableWidget
from PySide2 import QtGui
from PySide2.QtCore import Qt,QThread,Signal
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

	def setParms(self,*args):
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
		self.parms.extend(cmd[1:])
	#def setParms

	def run(self):
		cmd=[self.cmd]
		cmd.extend(self.parms)
		if "kcm" in cmd[0]:
			proc=self.accesshelper.launchKcmModule(self.cmd)
		else:
			proc=self.accesshelper.launchCmd(cmd)
		self.finished.emit(proc)
	#def run
#class thLauncher

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
		self.plasmaConfig={}
		self.hideControlButtons()
		self.locale=locale.getdefaultlocale()[0][0:2]
		self.rebost=store.client()
		self.launch=thLauncher()
		self.launch.finished.connect(self._endCmd)
	#def __init__

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.tblGrid=QTableTouchWidget()
		self.tblGrid.setColumnCount(3)
#		self.tblGrid.setShowGrid(False)
		self.tblGrid.verticalHeader().hide()
		self.tblGrid.horizontalHeader().hide()
		self.tblGrid.setSelectionBehavior(QTableWidget.SelectRows)
		self.tblGrid.setSelectionMode(QTableWidget.SingleSelection)
		self.tblGrid.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
		self.tblGrid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.tblGrid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.box.addWidget(self.tblGrid)
		self._renderGui()
	#def __initScreen__

	def _renderGui(self):
		self.tblGrid.setRowCount(0)
		self.tblGrid.setRowCount(2)
		btnAcce=QPushInfoButton()
		btnAcce.setText(i18n.get("ACCE"))
		btnAcce.setDescription(i18n.get("ACCEDSC"))
		btnAcce.loadImg("preferences-desktop-accessibility")
		self.tblGrid.setCellWidget(0,0,btnAcce)
		#self.tblGrid.verticalHeader().setSectionResizeMode(0,QHeaderView.ResizeToContents)
		btnAcce.clicked.connect(self._launch)
		btnOrca=QPushInfoButton()
		icons={}
		for app in ["orca","eviacam","antimicrox"]:
			appInfo=json.loads(self.rebost.showApp(app))
			if len(appInfo)>0:
				jInfo=json.loads(appInfo[0])
				icons.update({app:jInfo.get("icon","default")})
		btnOrca.setText(i18n.get("ORCA"))
		btnOrca.setDescription(i18n.get("ORCADSC"))
		btnOrca.loadImg(icons["orca"])
		self.tblGrid.setCellWidget(0,1,btnOrca)
		#self.tblGrid.verticalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
		btnOrca.clicked.connect(self._launch)
		btnLtts=QPushInfoButton()
		btnLtts.setText(i18n.get("LTTS"))
		btnLtts.setDescription(i18n.get("LTTSDSC"))
		btnLtts.loadImg("rsrc/ttsmanager.png")
		self.tblGrid.setCellWidget(0,2,btnLtts)
		btnLtts.clicked.connect(self._launch)
		btnDock=QPushInfoButton()
		btnDock.setText(i18n.get("DOCK"))
		btnDock.setDescription(i18n.get("DOCKDSC"))
		btnDock.loadImg("accesswizard")
		self.tblGrid.setCellWidget(1,0,btnDock)
		btnDock.clicked.connect(self._launch)
		btnJoys=QPushInfoButton()
		btnJoys.setText(i18n.get("ANTI"))
		btnJoys.setDescription(i18n.get("ANTIDSC"))
		btnJoys.loadImg(icons["antimicrox"])
		self.tblGrid.setCellWidget(1,1,btnJoys)
		btnJoys.clicked.connect(self._launch)
		btnEvia=QPushInfoButton()
		btnEvia.setText(i18n.get("EVIA"))
		btnEvia.setDescription(i18n.get("EVIADSC"))
		btnEvia.loadImg(icons["eviacam"])
		self.tblGrid.setCellWidget(1,2,btnEvia)
		btnEvia.clicked.connect(self._launch)
		self.tblGrid.horizontalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)

	def _launch(self,*args):
		args[0].setEnabled(False)
		if args[0].text()==i18n.get("ACCE"):
			mod="kcm_access"
			self.launch.setParms(mod)
			self.launch.start()
		else:
			if args[0].text()==i18n.get("ORCA"):
				cmd=self._getAppCmd("orca")
			elif args[0].text()==i18n.get("LTTS"):
				cmd=os.path.join(os.path.dirname(__file__),"..","tools","ttsmanager.py")
			elif args[0].text()==i18n.get("DOCK"):
				cmd=os.path.join(os.path.dirname(__file__),"..","dock","accessdock-config.py")
			elif args[0].text()==i18n.get("ANTI"):
				cmd=self._getAppCmd("antimicrox")
			elif args[0].text()==i18n.get("EVIA"):
				cmd=self._getAppCmd("eviacam")
			self.launch.setParms(cmd)
			self.launch.start()
	#def _launch

	def _endCmd(self,*args):
		for i in range(0,self.tblGrid.rowCount()):
			for j in range(0,self.tblGrid.columnCount()):
				wdg=self.tblGrid.cellWidget(i,j)
				if wdg.isEnabled()==False:
					wdg.setEnabled(True)
		
		print("++++++")
		print(args)
		print("++++++")
	#def _endCmd

	def _getAppCmd(self,app):
		cmdPath=self._getPathForCmd(app)
		if len(cmdPath)>0:
			cmd=[cmdPath]
			if cmdPath.endswith("/orca"):
				cmd.append("-s")
		else:
			cmd=["/usr/bin/appsedu","appstream://{}".format(app)]
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

	def updateScreen(self):
		pass
	#def updateScreen

