#!/usr/bin/python3
from PySide2.QtWidgets import QGridLayout
from PySide2 import QtGui
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem, QPushInfoButton,QTableTouchWidget
from wdg.configPane import QConfigPane
from extras.i18n import *

class effects(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("effects Load")
		self.setProps(shortDesc=i18n.get("EFFECT_MENU"),
		    description=i18n.get('EFFECT_DESCRIPTION'),
		    longDesc=i18n.get('EFFECT_DESCRIPTION'),
			icon="preferences-system-windows",
			tooltip=i18n.get("EFFECT_TOOLTIP"),
			index=2,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.hideControlButtons()
	#def __init__

	def _renderBtn(self,app):
		btn=QPushInfoButton()
		btn.defaultSize=72
		btn.label.setAlignment(Qt.AlignLeft)
		f=btn.font()
		if f.pointSize()<20:
			f.setPointSize(18)
		btn.setFont(f)
		for appName,data in app.items():
			btn.setText(i18n.get(appName))
			btn.setDescription(i18n.get(data[0]))
			btn.clicked.connect(lambda x:self._launch(appName))
			btn.loadImgSync(data[1])
		return(btn)
	#def _renderBtn

	def __initScreen__(self):
		lay=QGridLayout(self)
		apps=[{"NEFF":["kcm_kwin_effects","NEFFDSC","preferences-system-windows"]},
			{"DSCR":["kcm_kwin_scripts","DSCRDSC","preferences-plugin"]}
			]
		wdg=QConfigPane(apps)
		lay.addWidget(wdg,0,0,1,1)
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

	def updateScreen(self):
		pass
	#def updateScreen

