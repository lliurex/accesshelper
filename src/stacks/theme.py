#!/usr/bin/python3
from llxaccessibility import llxaccessibility
import os
from PySide6.QtWidgets import QApplication,QGridLayout,QListWidget,QListWidgetItem,QLabel
from PySide6 import QtGui
from PySide6.QtCore import Qt,QSize
from QtExtraWidgets import QStackedWindowItem, QPushInfoButton
import subprocess
import locale
import gettext
_ = gettext.gettext

i18n={
	"COLOR":_("Set global color scheme"),
	"COLORTXT":_("Color scheme"),
	"CONFIG":_("Appearance"),
	"DESCRIPTION":_("Look and feel options"),
	"FONTS":_("Configure system fonts"),
	"FONTSTXT":_("Fonts"),
	"LOOKF":_("Set global theme"),
	"LOOKFTXT":_("Theme"),
	"MENU":_("Appearance"),
	"MOUSE":_("Set cursor theme and size"),
	"MOUSETXT":_("Mouse"),
	"TOOLTIP":_("Appearance customizing"),
	}

class theme(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.setProps(shortDesc=i18n.get("MENU"),
		    description=i18n.get('DESCRIPTION'),
		    longDesc=i18n.get('DESCRIPTION'),
			icon="preferences-desktop-theme",
			tooltip=i18n.get("TOOLTIP"),
			index=3,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.plasmaConfig={}
		self.hideControlButtons()
		self.accesshelper=llxaccessibility.client()
		self.locale=locale.getdefaultlocale()[0][0:2]
		return(self)
	#def __init__

	def __initScreen__(self):
		lay=QGridLayout()
		self.lstApps=QListWidget()
		lay.addWidget(self.lstApps)
		self.setLayout(lay)
		self._renderGui()
	#def __initScreen__

	def _renderGui(self):
		controls=[]
		btnLookF=QPushInfoButton()
		controls.append(btnLookF)
		btnLookF.setText(i18n.get("LOOKFTXT"))
		btnLookF.setDescription(i18n.get("LOOKF"))
		btnLookF.loadImg("preferences-desktop-theme")
		btnLookF.clicked.connect(self._launch)
		btnColor=QPushInfoButton()
		controls.append(btnColor)
		btnColor.setText(i18n.get("COLORTXT"))
		btnColor.setDescription(i18n.get("COLOR"))
		btnColor.loadImg("preferences-desktop-color")
		btnColor.clicked.connect(self._launch)
		btnFonts=QPushInfoButton()
		controls.append(btnFonts)
		btnFonts.setText(i18n.get("FONTSTXT"))
		btnFonts.setDescription(i18n.get("FONTS"))
		btnFonts.loadImg("preferences-desktop-font")
		btnFonts.clicked.connect(self._launch)
		btnMouse=QPushInfoButton()
		controls.append(btnMouse)
		btnMouse.setText(i18n.get("MOUSETXT"))
		btnMouse.setDescription(i18n.get("MOUSE"))
		btnMouse.loadImg("preferences-desktop-mouse")
		btnMouse.clicked.connect(self._launch)
		for btn in controls:
			self.lstApps.addItem("")
			itm=self.lstApps.item(self.lstApps.count()-1)
			itm.setSizeHint(QSize(128,150))
			self.lstApps.setItemWidget(itm,btn)
	#def _renderGui

	def _launch(self,*args):
		args[0].setEnabled(False)
		QApplication.processEvents()
		if args[0].text()==_("Theme"):
			mod="kcm_desktoptheme"
		elif args[0].text()==_("Color scheme"):
			mod="kcm_colors"
		elif args[0].text()==_("Fonts"):
			mod="kcm_fonts"
		elif args[0].text()==_("Mouse"):
			mod="kcm_cursortheme"
		self.accesshelper.launchKcmModule(mod)
		args[0].setEnabled(True)
	#def _launch

	def updateScreen(self):
		pass
	#def updateScreen

