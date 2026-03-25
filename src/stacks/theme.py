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
	"COLO":_("Color scheme"),
	"COLODSC":_("Set global color scheme"),
	"CONFIG":_("Appearance"),
	"DESCRIPTION":_("Look and feel options"),
	"FONT":_("Fonts"),
	"FONTDSC":_("Configure system fonts"),
	"LOOK":_("Theme"),
	"LOOKDSC":_("Set global theme"),
	"MENU":_("Appearance"),
	"MICE":_("Mouse"),
	"MICEDSC":_("Set cursor theme and size"),
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
		self.lstApps.keyPressEvent2=self.lstApps.keyPressEvent
		self.lstApps.keyPressEvent=self.fakeKey
		lay.addWidget(self.lstApps)
		self.setLayout(lay)
		self._renderGui()
	#def __initScreen__

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
		btnLook=self._renderBtn("LOOK","LOOKDSC","preferences-desktop-theme")
		controls.append(btnLook)
		btnColr=self._renderBtn("COLO","COLODSC","preferences-desktop-color")
		controls.append(btnColr)
		btnFont=self._renderBtn("FONT","FONTDSC","preferences-desktop-font")
		controls.append(btnFont)
		btnMice=self._renderBtn("MICE","MICEDSC","preferences-desktop-mouse")
		controls.append(btnMice)
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

