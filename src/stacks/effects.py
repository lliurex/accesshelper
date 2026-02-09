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
		    longDesc=i18n.get('DESCRIPTION'),
			icon="preferences-system-windows",
			tooltip=i18n.get("TOOLTIP"),
			index=2,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.plasmaConfig={}
		self.hideControlButtons()
		self.locale=locale.getdefaultlocale()[0][0:2]
		#self.accesshelper=accesshelper.client()
		self.accesshelper=llxaccessibility.client()
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
		btnWneff=QPushInfoButton()
		controls.append(btnWneff)
		btnWneff.setText(i18n.get("EFFBTN"))
		btnWneff.setDescription(i18n.get("EFFDSC"))
		btnWneff.loadImg("preferences-system-windows")
		btnWneff.clicked.connect(self._launch)
		btnDseff=QPushInfoButton()
		controls.append(btnDseff)
		btnDseff.setText(i18n.get("DESBTN"))
		btnDseff.setDescription(i18n.get("DESDSC"))
		btnDseff.loadImg("preferences-plugin")
		btnDseff.clicked.connect(self._launch)
		for btn in controls:
			self.lstApps.addItem("")
			itm=self.lstApps.item(self.lstApps.count()-1)
			itm.setSizeHint(QSize(128,150))
			self.lstApps.setItemWidget(itm,btn)
	#def _renderGui

	def _launch(self,*args):
		args[0].setEnabled(False)
		QApplication.processEvents()
		mod=""
		if args[0].text()==i18n.get("EFFBTN"):
			mod="kcm_kwin_effects"
		elif args[0].text()==i18n.get("DESBTN"):
			mod="kcm_kwin_scripts"
		if len(mod)>0:
			self.accesshelper.launchKcmModule(mod)
		args[0].setEnabled(True)
	#def _launch

	def updateScreen(self):
		pass
	#def updateScreen

