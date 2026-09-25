#!/usr/bin/python3
from llxaccessibility import llxaccessibility
import os,shutil
import json
from PySide2.QtWidgets import QWidget,QGridLayout,QListWidget,QScrollArea
from PySide2 import QtGui
from PySide2.QtCore import Qt,QThread,Signal,QSize
from QtExtraWidgets import QStackedWindowItem, QPushInfoButton,QTableTouchWidget
from lib.threadLib import thLauncher
import subprocess
from rebost import store
from extras.i18n import *

class accessibility(QStackedWindowItem):
	back=Signal()
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.setProps(shortDesc=i18n.get("MENU"),
			description=i18n.get('DESCRIPTION'),
			longDesc=i18n.get('DESCRIPTION'),
			icon="preferences-desktop-accessibility",
			tooltip=i18n.get("TOOLTIP"),
			index=1,
			visible=True)
		self.enabled=True
		self.changed=[]
		self.rebost=store.client()
		self.hideControlButtons()
		self.thLauncher=thLauncher(self.rebost)
	#def __init__

	def _launch(self,*args):
		self.thLauncher.setParms(args[0])
		self.thLauncher.start()
	#def _launch

	def __initScreen__(self):
		lay=QGridLayout(self)
		wdg=QTableTouchWidget(0,1)
		wdg.horizontalHeader().hide()
		wdg.verticalHeader().hide()
		lay.addWidget(wdg,0,0,1,1)
		rsrcDir=os.path.join(os.path.dirname(os.path.realpath(__file__)),"..","rsrc")
		apps=[{"ACCE":["ACCEDSC","preferences-desktop-accessibility"]},
			{"ORCA":["ORCADSC",""]},
			{"LTTS":["LTTSDSC",os.path.join(rsrcDir,"ttsmanager.png")]},
			{"DOCK": ["DOCKDSC",os.path.join(rsrcDir,"accessdock.png")]},
			{"ANTI": ["ANTIDSC",""]},
			{"EVIA": ["EVIADSC",""]}
			]
		for app in apps:
			wdg.setRowCount(wdg.rowCount()+1)
			btn=self._renderBtn(app)
			btn.setMinimumWidth(wdg.size().width())
			btn.setFixedHeight(84)
			wdg.setCellWidget(wdg.rowCount()-1,0,btn)
			wdg.setRowHeight(wdg.rowCount()-1,btn.height()+20)
			btn.show()
		wdg.setColumnWidth(0,btn.width())
	#def __initScreen__

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
			if data[1]=="":
				appId=None
				if app=="ORCA":
					appId="orca"
				elif app=="EVIA":
					appId="eviacam"
				elif app=="ANTI":
					appId="antimicrox"
				if appId!=None:
					app=json.loads(self.rebost.showApp(appId))
					data[1]=app[0].get("icon")
			btn.clicked.connect(lambda x:self._launch(appName))
			btn.loadImgSync(data[1])
		return(btn)
	#def _renderBtn

	def updateScreen(self):
		pass
	#def updateScreen

