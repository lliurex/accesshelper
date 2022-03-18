#!/usr/bin/python3
import os,sys
from PySide2.QtWidgets import QApplication,QMessageBox,QGridLayout,QLabel,QPushButton,QWidget
from PySide2.QtCore import Qt,QSignalMapper
from stacks import libaccesshelper
import gettext
import time
import json
from app2menu import App2Menu
_ = gettext.gettext
QString=type("")
QInt=type(0)

class accessdock(QWidget):
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=True
		self.menu=App2Menu.app2menu()
		self.confFile="accessdock.json"
		self.confDir="/usr/share/accesshelper/"
		self.fastSettings={"color":"color","font_size":"","pointer_size":"","read":"","config":"","hide":""}
		self.widgets={}
		self.accesshelper=libaccesshelper.accesshelper()
		self._loadConfig()
		self._renderGui()
		self.x=0
		self.y=0
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("dock: {}".format(msg))
	#def _debug

	def _loadConfig(self):
		config=self._readConfig()
		if isinstance(config,dict):
			for setting,value in config.items():
				if setting=="hotkey":
					self._setHotkey(value)
	#def _loadConfig

	def _readConfig(self):
		config=""
		if os.path.isfile(os.path.join(self.confDir,self.confFile)):
			with open(os.path.join(self.confDir,self.confFile)) as f:
				config=json.loads(f.read())
		if os.path.isfile(os.path.join(os.environ.get('HOME'),".config",self.confFile)):
			with open(os.path.join(os.environ.get('HOME'),".config",self.confFile)) as f:
				config.update(json.loads(f.read()))
		return(config)
	#def _readConfig

	def _setHotkey(self,*args):
		data=args
		print(data)

	def _renderGui(self):
		#self.setWindowFlags(Qt.X11BypassWindowManagerHint)
		self.setWindowModality(Qt.WindowModal)
		self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
		layout=QGridLayout()
		col=0
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self.execute)
		for setting,value in self.fastSettings.items():
			lbl=QLabel(setting.replace("_"," ").capitalize())
			layout.addWidget(lbl,0,col,1,1)
			btn=QPushButton()
			sigmap_run.setMapping(btn,setting)
			btn.clicked.connect(sigmap_run.map)
			layout.addWidget(btn,1,col,1,1)
			self.widgets[setting]=btn
			col+=1

		self.setLayout(layout)
	#def _renderGui

	def execute(self,*args,**kwargs):
		if isinstance(args,tuple):
			if args[0].lower()=="hide":
				self.hide()
	#def execute

	def mousePressEvent(self, event):
		event.accept()
	#def mousePressEvent

	def mouseMoveEvent(self, e):
		x = e.globalX()-(self.width()/2)
		y = e.globalY()
		self.move(x, y)
	#def mouseMoveEvent
		

app=QApplication(["AccessDock"])
dock=accessdock()
dock.show()
app.exec_()
