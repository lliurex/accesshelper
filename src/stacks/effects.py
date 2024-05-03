#!/usr/bin/python3
#from appconfig import appconfigControls
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
	"CONFIG":_("Effects"),
	"DESBTN":_("Desktop plugins"),
	"DESDSC":_("Extra functionality for the desktop"),
	"EFFBTN":_("Windows effects"),
	"EFFDSC":_("Graphical effects for windows"),
	"MENU":_("Visual Effects"),
	"DESCRIPTION":_("Aids and visual effects"),
	"TOOLTIP":_("Aids and visual effects for improve system usability"),
	}

class effects(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.setProps(shortDesc=i18n.get("MENU"),
		    description=i18n.get('DESCRIPTION'),
			icon="preferences-system-windows",
			tooltip=i18n.get("TOOLTIP"),
			index=2,
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
		self.tblGrid.setRowCount(1)
		btnWneff=QPushInfoButton()
		btnWneff.setText(i18n.get("EFFBTN"))
		btnWneff.setDescription(i18n.get("EFFDSC"))
		btnWneff.loadImg("preferences-system-windows")
		self.tblGrid.setCellWidget(0,0,btnWneff)
		btnWneff.clicked.connect(self._launch)
		btnDseff=QPushInfoButton()
		btnDseff.setText(i18n.get("DESBTN"))
		btnDseff.setDescription(i18n.get("DESDSC"))
		btnDseff.loadImg("preferences-plugin")
		self.tblGrid.setCellWidget(0,1,btnDseff)
		btnDseff.clicked.connect(self._launch)
	#def _renderGui

	def _launch(self,*args):
		if args[0].text()==_("Window Effects"):
			mod="kcm_kwin_effects"
		elif args[0].text()==_("Desktop Effects"):
			mod="kcm_kwin_scripts"
		self.accesshelper.launchKcmModule(mod)
	#def _launch

	def updateScreen(self):
		pass
	#def updateScreen

