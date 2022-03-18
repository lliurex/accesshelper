#!/usr/bin/python3
import os,sys
from PySide2.QtWidgets import QApplication,QMessageBox,QGridLayout,QLabel,QPushButton,QWidget,QFrame,QDialog
from PySide2.QtCore import Qt,QSignalMapper
from stacks import libaccesshelper
from appconfig.appConfigStack import appConfigStack as confStack
from stacks.alpha import alpha
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
	#def _setKdeHotkey

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
			if setting=="font_size":
				btn.setText("{:.0f}".format(self.font().pointSizeF()))
			sigmap_run.setMapping(btn,setting)
			btn.clicked.connect(sigmap_run.map)
			layout2.addWidget(btn,1,col,1,1)
			self.widgets[setting]=btn
			col+=1
		self.setLayout(layout)
		self.move(self.coordx,self.coordy)
	#def _renderGui

	def execute(self,*args,**kwargs):
		if isinstance(args,tuple):
			if args[0].lower()=="hide":
				self.close()
			elif args[0].lower()=="color":
				alphaDlg=alpha(alpha)
				alphaDlg.move(self.coordx,self.coordy)
				alphaDlg._load_screen()
				alphaDlg.btn_ok.clicked.connect(alphaDlg.close)
				alphaDlg.btn_cancel.clicked.connect(alphaDlg.close)
				alphaDlg.setWindowModality(Qt.WindowModal)
				alphaDlg.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
				alphaDlg.show()
			elif args[0].lower()=="font_size":
				self._fontSize()
	#def execute

	def _fontSize(self):
		def moreSize(*args):
			font=lblTest.font()
			size=font.pointSizeF()+1
			font.setPointSizeF(size)
			lblTest.setFont(font)
		def lessSize(*args):
			font=lblTest.font()
			size=font.pointSizeF()-1
			font.setPointSizeF(size)
			lblTest.setFont(font)
			
		dlg=QDialog()
		lay=QGridLayout()
		dlg.setLayout(lay)
		frame=QFrame()
		frame.setFrameShape(QFrame.Panel)
		lay.addWidget(frame)
		lay2 = QGridLayout(frame)
		btnPlus=QPushButton("+")
		btnPlus.clicked.connect(moreSize)
		lay2.addWidget(btnPlus,0,0,1,1)
		btnMinus=QPushButton("-")
		btnMinus.clicked.connect(lessSize)
		lay2.addWidget(btnMinus,1,0,1,1)
		lblTest=QLabel("Texto de prueba")
		lblTest.setWordWrap(True)
		lay2.addWidget(lblTest,0,2,2,1)
		btnCancel=QPushButton("Cancel")
		btnCancel.clicked.connect(dlg.close)
		lay2.addWidget(btnCancel,2,0,2,1)
		btnOk=QPushButton("Apply")
		btnOk.clicked.connect(dlg.accept)
		lay2.addWidget(btnOk,2,2,1,1)
		dlg.move(self.coordx,self.coordy)
		dlg.setWindowModality(Qt.WindowModal)
		dlg.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
		change=dlg.exec()
		if change:
			qfont=lblTest.font()
			font=qfont.toString()
			minfont=font
			size=qfont.pointSize()
			minSize=size-2
			fontFixed="Hack"
			fixed="{0},{1},-1,5,50,0,0,0,0,0".format(fontFixed,size)
			if size>8:
				qfont.setPointSize(size-2)
				minFont=qfont.toString()
			self.accesshelper.setKdeConfigSetting("General","fixed",fixed,"kdeglobals")
			self.accesshelper.setKdeConfigSetting("General","font",font,"kdeglobals")
			self.accesshelper.setKdeConfigSetting("General","menuFont",font,"kdeglobals")
			self.accesshelper.setKdeConfigSetting("General","smallestReadableFont",minFont,"kdeglobals")
			self.accesshelper.setKdeConfigSetting("General","toolBarFont",font,"kdeglobals")
			self.accesshelper.setKdeConfigSetting("Appearance","Font",fixed,"Lliurex.profile")
			self.widgets["font_size"].setText("{:.0f}".format(size))

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
		self.coordx,self.coordy=(x,y)
		with open(os.path.join(os.environ.get('HOME'),".config",self.confFile),'w') as f:
			f.write(json.dumps(config,indent=4))
	#def mouseReleaseEvent

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
