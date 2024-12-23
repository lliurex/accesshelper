#!/usr/bin/python3
from llxaccessibility import llxaccessibility
import os
import json
from PySide6.QtWidgets import QApplication,QLabel,QGridLayout,QCheckBox,QSizePolicy,QRadioButton,QHeaderView,QTableWidgetItem,QAbstractScrollArea,QTableWidget
from PySide6 import QtGui
from PySide6.QtCore import Qt
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
		self.accesshelper=llxaccessibility.client()
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
		btnOrca.setText(i18n.get("ORCA"))
		btnOrca.setDescription(i18n.get("ORCADSC"))
		btnOrca.loadImg("orca")
		self.tblGrid.setCellWidget(0,1,btnOrca)
		#self.tblGrid.verticalHeader().setSectionResizeMode(1,QHeaderView.ResizeToContents)
		btnOrca.clicked.connect(self._launch)
		btnLtts=QPushInfoButton()
		btnLtts.setText(i18n.get("LTTS"))
		btnLtts.setDescription(i18n.get("LTTSDSC"))
		btnLtts.loadImg("kmouth")
		self.tblGrid.setCellWidget(0,2,btnLtts)
		#self.tblGrid.verticalHeader().setSectionResizeMode(2,QHeaderView.ResizeToContents)
		btnLtts.clicked.connect(self._launch)
		btnDock=QPushInfoButton()
		btnDock.setText(i18n.get("DOCK"))
		btnDock.setDescription(i18n.get("DOCKDSC"))
		btnDock.loadImg("accesswizard")
		btnDock.setMinimumWidth(btnDock.width())
		btnDock.setMinimumHeight(btnDock.height())
		self.tblGrid.setCellWidget(1,0,btnDock)
		btnDock.clicked.connect(self._launch)
		btnJoys=QPushInfoButton()
		btnJoys.setText(i18n.get("ANTI"))
		btnJoys.setDescription(i18n.get("ANTIDSC"))
		btnJoys.loadImg("io.github.antimicrox.antimicrox")
		btnJoys.setMinimumWidth(btnJoys.width())
		btnJoys.setMinimumHeight(btnJoys.height())
		self.tblGrid.setCellWidget(1,1,btnJoys)
		btnJoys.clicked.connect(self._launch)
		btnEvia=QPushInfoButton()
		btnEvia.setText(i18n.get("EVIA"))
		btnEvia.setDescription(i18n.get("EVIADSC"))
		btnEvia.loadImg("eviacam")
		btnEvia.setMinimumWidth(btnEvia.width())
		btnEvia.setMinimumHeight(btnEvia.height())
		self.tblGrid.setCellWidget(1,2,btnEvia)
		btnEvia.clicked.connect(self._launch)
	#	self.tblGrid.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)

	def _launch(self,*args):
		args[0].setEnabled(False)
		if args[0].text()==i18n.get("ACCE"):
			mod="kcm_access"
			self.accesshelper.launchKcmModule(mod,mp=True)
		else:
			if args[0].text()==i18n.get("ORCA"):
				cmd="orca","-s"
			elif args[0].text()==i18n.get("LTTS"):
				cmd=os.path.join(os.path.dirname(__file__),"..","tools","ttsmanager.py")
			elif args[0].text()==i18n.get("DOCK"):
				cmd=os.path.join(os.path.dirname(__file__),"..","dock","accessdock-config.py")
			elif args[0].text()==i18n.get("ANTI"):
				cmd=self._getAppPath("antimicrox")
			elif args[0].text()==i18n.get("EVIA"):
				cmd=self._getAppPath("eviacam")
			self.accesshelper.launchCmd(cmd,mp=True)
	#def _launch

	def _getAppPath(self,app):
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
	#def _getAntiMicroPath

	def updateScreen(self):
		pass
	#def updateScreen

