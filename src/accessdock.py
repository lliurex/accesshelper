#!/usr/bin/python3
import os,sys
from PySide2.QtWidgets import QApplication,QMessageBox,QGridLayout,QLabel,QPushButton,QWidget,QFrame
from PySide2.QtCore import Qt,QSignalMapper
from stacks import libaccesshelper
import gettext
import signal
import time
import json
from app2menu import App2Menu
_ = gettext.gettext
QString=type("")
QInt=type(0)



class accessdock(QWidget):

	def __init__(self,*args,**kwargs):
		super().__init__()
		signal.signal(signal.SIGUSR1,self.handler)
		self.dbg=True
		self.menu=App2Menu.app2menu()
		self.confFile="accessdock.json"
		self.confDir="/usr/share/accesshelper/"
		self.fastSettings={"color":"color","font_size":"","pointer_size":"","read":"","config":"","hide":""}
		self.widgets={}
		self.accesshelper=libaccesshelper.accesshelper()
		self.coordx=0
		self.coordy=0
		self._loadConfig()
		self._renderGui()
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("dock: {}".format(msg))
	#def _debug
	def handler(self,signal_received, frame):
		print('SIGINT or CTRL-C detected. Exiting gracefully')

	def _loadConfig(self):
		config=self._readConfig()
		if isinstance(config,dict):
			if config.get("hotkey",""):
				hotkey=str(config.get("hotkey"))
			else:
				hotkey="Ctrl+Space"
			if config.get("coords",""):
				self.coordx,self.coordy=config.get("coords")
			self._setKdeHotkey(hotkey)
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

	def _setKdeHotkey(self,*args):
		data=[]
		desc="{0},{0},show accessdock".format(args[0])
		data.append(("_launch",desc))
		data.append(("_k_friendly_name","accessdock"))
		config={'kglobalshortcutsrc':{'accessdock.desktop':data}}
		self.accesshelper.setSystemConfig(config)

	def _renderGui(self):
		#self.setWindowFlags(Qt.X11BypassWindowManagerHint)
		self.setWindowModality(Qt.WindowModal)
		self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
		layout=QGridLayout()
		frame=QFrame()
		frame.setFrameShape(QFrame.Panel)
		layout.addWidget(frame)
		layout2 = QGridLayout(frame)
		col=0
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self.execute)
		for setting,value in self.fastSettings.items():
			lbl=QLabel(setting.replace("_"," ").capitalize())
			layout2.addWidget(lbl,0,col,1,1)
			btn=QPushButton()
			sigmap_run.setMapping(btn,setting)
			btn.clicked.connect(sigmap_run.map)
			layout2.addWidget(btn,1,col,1,1)
			self.widgets[setting]=btn
			col+=1

		self.setLayout(layout)
		print("MOVE TO {} {}".format(self.coordx,self.coordy))
		self.move(self.coordx,self.coordy)
	#def _renderGui

	def execute(self,*args,**kwargs):
		if isinstance(args,tuple):
			if args[0].lower()=="hide":
				self.close()
	#def execute

	def mousePressEvent(self, event):
		event.accept()
	#def mousePressEvent

	def mouseMoveEvent(self, e):
		x = e.globalX()-(self.width()/2)
		y = e.globalY()
		self.move(x, y)
	#def mouseMoveEvent

	def mouseReleaseEvent(self, e):
		x = e.globalX()-(self.width()/2)
		y = e.globalY()
		config={}
		if os.path.isfile(os.path.join(os.environ.get('HOME'),".config",self.confFile)):
			with open(os.path.join(os.environ.get('HOME'),".config",self.confFile),'r') as f:
				config.update(json.loads(f.read()))
		config={"coords":[x,y]}
		with open(os.path.join(os.environ.get('HOME'),".config",self.confFile),'w') as f:
			f.write(json.dumps(config,indent=4))
	#def mousePressEvent

if os.path.isfile("/tmp/.accessdock.pid"):
	kill=True
	try:
		pid=int(open("/tmp/.accessdock.pid").read())
	except:
		kill=False
	if kill:
		try:
			os.kill(pid,signal.SIGUSR1)
		except:
			kill=False
	if kill:
		sys.exit(0)

with open("/tmp/.accessdock.pid","w") as f:
	f.write("{}".format(os.getpid()))

app=QApplication(["AccessDock"])
dock=accessdock()
dock.show()
app.exec_()
