#!/usr/bin/python3
from . import accesshelper
#from appconfig import appconfigControls
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
	"COLOR":_("Set global color scheme"),
	"CONFIG":_("Appearance"),
	"DESCRIPTION":_("Look and feel options"),
	"FONTS":_("Configure system fonts"),
	"LOOKF":_("Set global theme"),
	"MENU":_("Appearance"),
	"MOUSE":_("Set cursor theme and size"),
	"TOOLTIP":_("Appearance customizing"),
	}

class theme(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.setProps(shortDesc=i18n.get("MENU"),
		    description=i18n.get('DESCRIPTION'),
			icon="preferences-desktop-theme",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.plasmaConfig={}
		self.accesshelper=accesshelper.client()
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
		btnLookF=QPushInfoButton()
		btnLookF.setText("Theme")
		btnLookF.setDescription(i18n.get("LOOKF"))
		btnLookF.loadImg("preferences-desktop-theme")
		self.tblGrid.setCellWidget(0,0,btnLookF)
		btnLookF.clicked.connect(self._launch)
		btnColor=QPushInfoButton()
		btnColor.setText("Color Scheme")
		btnColor.setDescription(i18n.get("COLOR"))
		btnColor.loadImg("preferences-desktop-color")
		self.tblGrid.setCellWidget(0,1,btnColor)
		btnColor.clicked.connect(self._launch)
		btnFonts=QPushInfoButton()
		btnFonts.setText("Fonts")
		btnFonts.setDescription(i18n.get("FONTS"))
		btnFonts.loadImg("preferences-desktop-font")
		self.tblGrid.setCellWidget(0,2,btnFonts)
		btnFonts.clicked.connect(self._launch)
		btnMouse=QPushInfoButton()
		btnMouse.setText("Mouse")
		btnMouse.setDescription(i18n.get("MOUSE"))
		btnMouse.loadImg("preferences-desktop-mouse")
		self.tblGrid.setCellWidget(1,0,btnMouse)
		btnMouse.clicked.connect(self._launch)
	#def _renderGui

	def _launch(self,*args):
		if args[0].text()==_("Theme"):
			mod="kcm_desktoptheme"
		elif args[0].text()==_("Color Scheme"):
			mod="kcm_colors"
		elif args[0].text()==_("Fonts"):
			mod="kcm_fonts"
		elif args[0].text()==_("Mouse"):
			mod="kcm_cursortheme"
		self.accesshelper.launchKcmModule(mod,mp=True)
	#def _launch

	def updateScreen(self):
		pass
	#def updateScreen

