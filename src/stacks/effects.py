#!/usr/bin/python3
from llxaccessibility import llxaccessibility
import os
from PySide2.QtWidgets import QApplication,QGridLayout,QListWidget,QListWidgetItem,QLabel
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize
from QtExtraWidgets import QStackedWindowItem, QPushInfoButton
import subprocess
import locale
import gettext
_ = gettext.gettext

i18n={
	"CONFIG":_("Effects"),
	"DSCR":_("Desktop plugins"),
	"DSCRDSC":_("Extra functionality for the desktop"),
	"NEFF":_("Windows effects"),
	"NEFFDSC":_("Graphical effects for windows"),
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
		self.lstApps.keyPressEvent2=self.lstApps.keyPressEvent
		self.lstApps.keyPressEvent=self.fakeKey
		lay.addWidget(self.lstApps)
		self.setLayout(lay)
		self._renderGui()
	#def __initScreen__

	def _launch(self,*args):
		args[0].setEnabled(False)
		QApplication.processEvents()
		mod=""
		if args[0].text()==i18n.get("NEFF"):
			mod="kcm_kwin_effects"
		elif args[0].text()==i18n.get("DSCR"):
			mod="kcm_kwin_scripts"
		if len(mod)>0:
			self.accesshelper.launchKcmModule(mod)
		args[0].setEnabled(True)
	#def _launch

	def fakeKey(self,*args):
		ev=args[0]
		if ev.key()==Qt.Key_Left:
			self.parent.lstNav.setFocus()
		else:
			self.lstApps.keyPressEvent2(*args)
			ev.ignore()
		return True
	#def fakeKey

	def focusInEvent(self,*args):
		self.lstApps.setFocus()
	#def focusInEvent


	def _renderBtn(self,i18Text,i18Desc,img=""):
		btn=QPushInfoButton()
		btn.setText(i18n.get(i18Text))
		btn.setDescription(i18n.get(i18Desc))
		if img!="":
			btn.loadImg(img)
		btn.clicked.connect(self._launch)
		return(btn)
	#def _renderBtn

	def _renderGui(self):
		controls=[]
		btnWnef=self._renderBtn("NEFF","NEFFDSC","preferences-system-windows")
		controls.append(btnWnef)
		btnDsef=self._renderBtn("DSCR","DSCRDSC","preferences-plugin")
		controls.append(btnDsef)
		for btn in controls:
			self.lstApps.addItem("")
			itm=self.lstApps.item(self.lstApps.count()-1)
			itm.setSizeHint(QSize(128,150))
			self.lstApps.setItemWidget(itm,btn)
	#def _renderGui

	def updateScreen(self):
		pass
	#def updateScreen

