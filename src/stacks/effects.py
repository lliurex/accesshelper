#!/usr/bin/python3
#from appconfig import appconfigControls
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
	"CONFIG":_("Effects"),
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
		return(self)
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

	def _launch(self,*args):
		if args[0].text()==_("Window Effects"):
			cmd=["kcmshell5","kcm_kwin_effects"]
		elif args[0].text()==_("Desktop Effects"):
			cmd=["kcmshell5","kcm_kwin_scripts"]
		subprocess.run(cmd)
	#def _launch

	def updateScreen(self):
		self.tblGrid.setRowCount(0)
		self.tblGrid.setRowCount(1)
		btnWneff=QPushInfoButton()
		btnWneff.setText("Window Effects")
		btnWneff.setDescription("Graphical effects")
		btnWneff.loadImg("preferences-system-windows")
		self.tblGrid.setCellWidget(0,0,btnWneff)
		btnWneff.clicked.connect(self._launch)
		btnDseff=QPushInfoButton()
		btnDseff.setText("Desktop Effects")
		btnDseff.loadImg("preferences-plugin")
		self.tblGrid.setCellWidget(0,1,btnDseff)
		btnDseff.clicked.connect(self._launch)
		self.tblGrid.verticalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
		self.tblGrid.verticalHeader().setSectionResizeMode(1,QHeaderView.Stretch)
	#def updateScreen

