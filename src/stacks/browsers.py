#!/usr/bin/python3
from llxaccessibility import llxaccessibility
from app2menu import App2Menu
import os,shutil
import json
from PySide2.QtWidgets import QApplication,QGridLayout,QListWidget,QListWidgetItem,QLabel,QWidget,QComboBox
from PySide2 import QtGui
from PySide2.QtCore import Qt,QThread,Signal,QSize
from QtExtraWidgets import QStackedWindowItem, QPushInfoButton
import subprocess
from rebost import store
import gettext
_ = gettext.gettext

i18n={
	"CONFIG":_("Browser addons"),
	"MENU":_("Browser addons"),
	"DESCRIPTION":_("Accesible browsing"),
	"TOOLTIP":_("Settings and addons for improved browser accessibility")
	}

class thLauncher(QThread):
	finished=Signal("PyObject")
	def __init__(self,parent=None,*args,**kwargs):
		super().__init__()
		self.accesshelper=llxaccessibility.client()
		self.cmd=""

	def setParms(self,*args):
		self.cmd=args[0]
	#def setParms

	def run(self):
		proc=self.accesshelper.launchCmd(self.cmd)
		self.finished.emit(proc)
	#def run
#class thLauncher

class browsers(QStackedWindowItem):
	back=Signal()
	def __init_stack__(self):
		self.dbg=True
		self._debug("browser Load")
		self.setProps(shortDesc=i18n.get("MENU"),
			description=i18n.get('DESCRIPTION'),
			longDesc=i18n.get('DESCRIPTION'),
			icon="preferences-system-network",
			tooltip=i18n.get("TOOLTIP"),
			index=4,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.launch=thLauncher()
		self.launch.finished.connect(self._endCmd)
		self.hideControlButtons()
	#def __init__

	def __initScreen__(self):
		lay=QGridLayout()
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

	def _defCmbBrowsers(self):
		cmb=QComboBox()
		cmb.setIconSize(QSize(64,64))
		cmb.activated.connect(self.updateScreen)
		xdg=App2Menu.app2menu()
		browsers=xdg.get_apps_for_mime("text/html")
		default=xdg.get_default_app_for_file("index.html")
		defIndex=-1
		for b in browsers:
			lbl=QLabel()
			bicn=b.get("Icon","internet-web-browser")
			icn=QtGui.QIcon.fromTheme(bicn)
			cmb.addItem(icn," {}".format(b["Name"]))
			data=os.path.basename(b["Exec"]).split(" ")[0]
			cmb.setItemData(cmb.count()-1,data,Qt.UserRole)
			if default in b["Exec"]:
				defIndex=cmb.count()-1
		cmb.setCurrentIndex(defIndex)
		return(cmb)
	#def _defCmbBrowsers

	def _renderGui(self):
		self.cmbBrowsers=self._defCmbBrowsers()
		self.layout().addWidget(self.cmbBrowsers,0,0,1,1,Qt.AlignLeft)
		self.lstApps=QListWidget()
		self.lstApps.keyPressEvent2=self.lstApps.keyPressEvent
		self.lstApps.keyPressEvent=self.fakeKey
		self.layout().addWidget(self.lstApps)
		self.updateScreen()
	#def _renderGui

	def _getAddonsForBrowser(self,*args):
		data=self.cmbBrowsers.itemData(self.cmbBrowsers.currentIndex(),Qt.UserRole)
		faddons="/usr/share/accesswizard/rsrc/browsers.json"
		jcontent={}
		addons=[]
		if os.path.isfile(faddons):
			fcontent=""
			with open(faddons,"r") as f:
				fcontent=f.read()
			jcontent=json.loads(fcontent)
		if data in jcontent:
			for addon in jcontent[data]:
				addons.append(addon)
		return(addons)
	#def _getAddonsForBrowser

	def _endCmd(self,*args):
		for i in range(0,self.lstApps.count()):
			itm=self.lstApps.item(i)
			wdg=self.lstApps.itemWidget(itm)
			wdg.setEnabled(True)
	#def _endCmd

	def _launch(self,*args):
		data=self.cmbBrowsers.itemData(self.cmbBrowsers.currentIndex(),Qt.UserRole)
		args[0].setEnabled(False)
		self.launch.setParms([data,args[0].toolTip()])
		self.launch.start()
	#def _launch

	def _renderBtn(self,name,desc,url="",img=""):
		btn=QPushInfoButton()
		btn.setText(name)
		font=btn.label.font()
		size=font.pointSize()
		size+=4
		btn.label.setFont(font)
		btn.setDescription(desc)
		btn.setToolTip(url)
		if img!="":
			btn.loadImg(img)
		btn.clicked.connect(self._launch)
		return(btn)
	#def _renderBtn

	def updateScreen(self,browser=None):
		self.lstApps.clear()
		addons=self._getAddonsForBrowser()
		oldCursor=self.cursor()
		for addon in addons:
			self.setCursor(Qt.WaitCursor)
			btn=self._renderBtn(addon["name"],addon["desc"],addon["url"],addon["icon"])
			self.lstApps.addItem("")
			itm=self.lstApps.item(self.lstApps.count()-1)
			itm.setSizeHint(QSize(228,150))
			self.lstApps.setItemWidget(itm,btn)
		self.setCursor(oldCursor)
	#def updateScreen

