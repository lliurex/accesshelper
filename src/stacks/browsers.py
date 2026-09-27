#!/usr/bin/python3
from app2menu import App2Menu
import os,json
from PySide2.QtWidgets import QGridLayout,QComboBox,QLabel
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSize
from QtExtraWidgets import QStackedWindowItem
from wdg.configPane import QConfigPane
from extras.i18n import *

class browsers(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=True
		self._debug("browser Load")
		self.setProps(shortDesc=i18n.get("BROWSER_MENU"),
			description=i18n.get('BROWSER_DESCRIPTION'),
			longDesc=i18n.get('BROWSER_DESCRIPTION'),
			icon="preferences-system-network",
			tooltip=i18n.get("BROWSER_TOOLTIP"),
			index=4,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.hideControlButtons()
	#def __init__

	def _showAddonsForBrowser(self,*args):
		for pane in self.wdgBrowsers.values():
			pane.hide()
		pane=self.wdgBrowsers.get(args[0],None)
		if pane!=None:
			pane.show()
	#def _showAddonsForBrowser

	def _defCmbBrowsers(self):
		cmb=QComboBox()
		cmb.setIconSize(QSize(64,64))
		cmb.activated.connect(self._showAddonsForBrowser)
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

	def _getAddonsForBrowser(self,*args):
		#data=self.cmbBrowsers.itemData(self.cmbBrowsers.currentIndex(),Qt.UserRole)
		faddons="/usr/share/accesswizard/rsrc/browsers.json"
		jcontent={}
		if os.path.isfile(faddons):
			fcontent=""
			with open(faddons,"r") as f:
				fcontent=f.read()
			jcontent=json.loads(fcontent)
		return(jcontent)
	#def _getAddonsForBrowser

	def __initScreen__(self):
		lay=QGridLayout(self)
		self.cmbBrowsers=self._defCmbBrowsers()
		self.wdgBrowsers={}
		lay.addWidget(self.cmbBrowsers,0,0,1,1,Qt.AlignLeft|Qt.AlignTop)
		addons=self._getAddonsForBrowser()
		for idx in range(0,self.cmbBrowsers.count()):
			apps=[]
			browser=self.cmbBrowsers.itemData(idx,Qt.UserRole)
			data=browser
			if "chrome" in browser:
				data=="chromium"
			for addonData in addons.get(data,[]):
				cmd="{0} {1}".format(browser,addonData.get("url",""))
				app={addonData.get("name"):[cmd,addonData.get("desc"),addonData.get("icon")]}
				apps.append(app)
			wdg=QConfigPane(apps)
			self.wdgBrowsers[idx]=wdg
			lay.addWidget(wdg,1,0,1,1)
			wdg.hide()
		self.cmbBrowsers.setCurrentIndex(0)
		self._showAddonsForBrowser(0)
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

	def updateScreen(self,browser=None):
		pass
	#def updateScreen

