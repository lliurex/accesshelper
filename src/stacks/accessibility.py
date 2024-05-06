#!/usr/bin/python3
from . import accesshelper
import os
from PySide2.QtWidgets import QApplication,QLabel,QGridLayout,QCheckBox,QSizePolicy,QRadioButton,QHeaderView,QTableWidgetItem,QAbstractScrollArea
from PySide2 import QtGui
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem, QTableTouchWidget, QPushInfoButton
import subprocess
import locale
import gettext
_ = gettext.gettext

i18n={
	"ACCE":_("System Accessibility"),
	"ACCEDSC":_("Plasma Accessibility module"),
	"CONFIG":_("Accessibility"),
	"DOCK":_("Accessibility Dock"),
	"DOCKDSC":_("Dock with customizable fast actions"),
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
			icon="preferences-desktop-accessibility",
			tooltip=i18n.get("TOOLTIP"),
			index=3,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.plasmaConfig={}
		self.locale=locale.getdefaultlocale()[0][0:2]
		self.accesshelper=accesshelper.client()
	#def __init__

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.tblGrid=QTableTouchWidget()
		self.tblGrid.setColumnCount(3)
#		self.tblGrid.setShowGrid(False)
		self.tblGrid.verticalHeader().hide()
		self.tblGrid.horizontalHeader().hide()
		self.tblGrid.setSelectionBehavior(self.tblGrid.SelectRows)
		self.tblGrid.setSelectionMode(self.tblGrid.SingleSelection)
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
		btnDock.loadImg("accesswdock")
		btnDock.setMinimumWidth(btnDock.width())
		btnDock.setMinimumHeight(btnDock.height())
		self.tblGrid.setCellWidget(1,0,btnDock)
		btnDock.clicked.connect(self._launch)
	#	self.tblGrid.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)

	def _launch(self,*args):
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
			self.accesshelper.launchCmd(cmd,mp=True)
	#def _launch

	def updateScreen(self):
		pass
	#def updateScreen

