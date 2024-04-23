#!/usr/bin/python3
import os
from PySide2.QtWidgets import QApplication,QLabel,QGridLayout,QCheckBox,QSizePolicy,QRadioButton,QHeaderView,QTableWidgetItem
from PySide2 import QtGui
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem, QTableTouchWidget, QPushInfoButton
import subprocess
import locale
import gettext
_ = gettext.gettext

i18n={
	"CONFIG":_("Settings"),
	"MENU":_("Other Settings"),
	"DESCRIPTION":_("Other options"),
	"TOOLTIP":_("Advanced settings"),
	}

class settings(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.setProps(shortDesc=i18n.get("MENU"),
		    description=i18n.get('DESCRIPTION'),
			icon="preferences-other",
			tooltip=i18n.get("TOOLTIP"),
			index=4,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.plasmaConfig={}
		self.locale=locale.getdefaultlocale()[0][0:2]
	#def __init__

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.tblGrid=QTableTouchWidget()
		self.tblGrid.setColumnCount(3)
#		self.tblGrid.setShowGrid(False)
		self.tblGrid.verticalHeader().hide()
		self.tblGrid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		#self.tblGrid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.tblGrid.horizontalHeader().hide()
		self.tblGrid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.tblGrid.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
		self.tblGrid.horizontalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
		self.tblGrid.horizontalHeader().setSectionResizeMode(2,QHeaderView.Stretch)
		self.tblGrid.setSelectionBehavior(self.tblGrid.SelectRows)
		self.tblGrid.setSelectionMode(self.tblGrid.SingleSelection)
		self.box.addWidget(self.tblGrid)
	#def __initScreen__

	def updateScreen(self):
		self.tblGrid.setRowCount(0)
		self.tblGrid.setRowCount(2)
		chkGrub=QCheckBox(i18n("GRUB"))
		self.tblGrid.setCellWidget(0,0,chkGrub)
		self.tblGrid.verticalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
		self.tblGrid.verticalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
	#def updateScreen

