#!/usr/bin/python3
import os,sys,io,psutil,shutil,signal,time
from PySide2.QtWidgets import QApplication,QMessageBox,QGridLayout,QLabel,QToolButton,QWidget,QFrame,QDialog,QPushButton,QComboBox
from PySide2.QtCore import Qt,QSignalMapper,QSize,QThread
from PySide2.QtGui import QIcon,QPixmap,QCursor
from stacks import libaccesshelper
from stacks import libspeechhelper as speech
from appconfig.appConfigStack import appConfigStack as confStack
from stacks.alpha import alpha
import json
import subprocess
import string
from app2menu import App2Menu
import gettext
gettext.textdomain('access_helper')
_ = gettext.gettext
QString=type("")
QInt=type(0)

class speaker(QThread):
	def __init__(self,parent,speech):
		QThread.__init__(self, parent)
		self.parent=parent
		self.clipboard=True
		self.play=False
		self.prc=0
		self.speech=speech
		self.btn=None
		self.icn=None
	
	def run(self):
		#self.parent.hide()
		self.play=True
		if self.btn:
			self.btn.setEnabled(False)
		if self.clipboard==True:
			self.prc=self.speech.readScreen(onlyClipboard=True)
		else:
			self.prc=self.speech.readScreen(onlyScreen=True)
		if self.btn:
			self.btn.setEnabled(True)
		if isinstance(self.prc,int)==False:
			self.prc.communicate()
		#self.parent.show()
		self.play=False
		if self.btn:
			self.btn.setEnabled(True)
			if self.icn:
				self.btn.setIcon(self.icn)
	
	def stop(self):
		if isinstance(self.prc,int)==False:
			os.kill(self.prc.pid,signal.SIGINT)
			self.prc.communicate()
		self.wait()
		self.play=False
		if self.btn:
			self.btn.setEnabled(True)

class accessdock(QWidget):
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=True
		self._chkDockRunning()
		self.menu=App2Menu.app2menu()
		self.confFile="accesshelper.json"
		self.confDir="/usr/share/accesshelper/"
		#self.fastSettings={"color":"color","scale":"","read":"","capture":"","osk":"","config":"","hide":""}
		self.fastSettings={"color":"color","scale":"","font_size":"","pointer_size":"","read":"","capture":"","osk":"","config":"","hide":""}
		self.widgets={}
		self.accesshelper=libaccesshelper.accesshelper()
		self.speech=speech.speechhelper()
		self.coordx=0
		self.coordy=0
		self.rate=0
		self.pitch=50
		self.readIcn=""
		self.captureIcn=""
		self.cancelIcn=QIcon.fromTheme("media-playback-stop")
		self.speaker=speaker(self,self.speech)
		self._loadConfig()
		self._renderGui()
		self.fontSize=""
	#def __init__

	def closeEvent(self, event):
		sys.exit(0)
	#def closeEvent(self, event):

	def _debug(self,msg):
		if self.dbg:
			print("dock: {}".format(msg))
	#def _debug

	def _chkDockRunning(self):
		ps=list(psutil.process_iter())
		count=0
		for p in ps:
			if "accessdock" in str(p.name):
				self._debug("Accessdock is running as pid {}".format(p.pid))
				if p.pid!=os.getpid():
					os.kill(p.pid,signal.SIGKILL)
	#def _chkDockRunning

	def _loadConfig(self):
		config=self._readConfig()
		if isinstance(config,dict):
			hotkey="Ctrl+Space"
			if config.get("dockHk",""):
				hotkey=str(config.get("dockHk"))
			else:
				(mainHk,hkData,hkSetting,hkSection)=self.accesshelper.getHotkey("accessdock.desktop")
				if mainHk!="":
					hotkey=mainHk
			if config.get("coords",""):
				self.coordx,self.coordy=config.get("coords")
			else:
				cursorPosition =QCursor.pos()
				self.coordx,self.coordy=cursorPosition.x(),cursorPosition.y()
			speed=config.get("speed","1x")
			self.fonts=config.get("fonts","")
			self.pitch=config.get("pitch","50")
			speed=speed.replace("x","")
			#eSpeak min speed=80 max speed=390
			self.rate=self.speech.setRate(float(speed))
			self.voice=config.get("voice","JuntaDeAndalucia_es_pa_diphone")
			self.speech.setVoice(self.voice)
			self._setKdeHotkey(hotkey)
			self.xscale=config.get("xscale","100")
			if os.path.isfile("/tmp/.xscale"):
				scale="0"
				with open("/tmp/.xscale","r") as f:
					scaleid=f.read()
					scale=scaleid.split("=")[0]
					sessionid=scaleid.split("=")[-1].strip()
				if len(scale)==3 and str(sessionid)==str(os.environ.get("XDG_SESSION_ID","")):
					self.xscale=scale
		home=os.environ.get("HOME")
		onboard="/usr/share/accesshelper/onboard.dconf"
		if os.path.isfile(os.path.join(home,".config/accesshelper/onboard.dconf"))==False:
			if os.path.isfile(onboard):
				shutil.copy(onboard,os.path.join(home,".config/accesshelper/onboard.dconf"))
			else:
				cmd=["dconf","dump","/org/onboard/"]
				fout=open(os.path.join(home,".config/accesshelper/onboard.dconf"),"wb")
				subprocess.run(cmd,stdout=fout)
		else:
			cmd=["dconf","dump","/org/onboard/"]
			fout=open(os.path.join(home,".config/accesshelper/onboard.dconf"),"wb")
			subprocess.run(cmd,stdout=fout)
			
	#def _loadConfig

	def _readConfig(self):
		config={}
		if os.path.isfile(os.path.join(self.confDir,self.confFile)):
			with open(os.path.join(self.confDir,self.confFile)) as f:
				config=json.loads(f.read())
		if os.path.isfile(os.path.join(os.environ.get('HOME'),".config","accesshelper",self.confFile)):
			with open(os.path.join(os.environ.get('HOME'),".config","accesshelper",self.confFile)) as f:
				config.update(json.loads(f.read()))
		return(config)
	#def _readConfig

	def _setKdeHotkey(self,*args):
		data=[]
		desc="{0},{0},show accessdock".format(args[0])
		data.append(("_launch",desc))
		data.append(("_k_friendly_name","accessdock"))
		config={'kglobalshortcutsrc':{'accessdock.desktop':data}}
		self.accesshelper.setPlasmaConfig(config)
	#def _setKdeHotkey

	def _renderGui(self):
		#self.setWindowFlags(Qt.X11BypassWindowManagerHint)
		self.setWindowModality(Qt.WindowModal)
		self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint|Qt.Tool)
		layout=QGridLayout()
		frame=QFrame()
		frame.setFrameShape(QFrame.Panel)
		layout.addWidget(frame)
		layout2 = QGridLayout(frame)
		col=0
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self.execute)
		for setting,value in self.fastSettings.items():
			#lbl=QLabel(setting.replace("_"," ").capitalize())
			#layout2.addWidget(lbl,0,col,1,1)
			btn=QToolButton()
			btnSize=QSize(256,72)
			btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
			self._assignButton(setting,btn)
			sigmap_run.setMapping(btn,setting)
			btn.clicked.connect(sigmap_run.map)
			btn.setMaximumSize(btnSize)
			layout2.addWidget(btn,0,col,1,1,Qt.AlignLeft)
			self.widgets[setting]=btn
			col+=1
		sizes=[]
		for desc,btn in self.widgets.items():
			sizes.append(btn.sizeHint().width())
		sizes.sort()
		for desc,btn in self.widgets.items():
			btn.setMinimumWidth(int(sizes[-2]))
		self.setLayout(layout)
		self.move(self.coordx,self.coordy)
	#def _renderGui

	def _assignButton(self,setting,btn):
		if setting=="font_size":
			btn.setText("{:.0f}px\nFont".format(self.font().pointSizeF()))
			btn.setToolTip(_("Set font size"))
		if setting=="scale":
			#icn=QIcon.fromTheme("zoom-in")
			btn.setText(_("{}%\nScale").format(self.xscale))
			btn.setToolTip(_("Set screen scale"))
			#btn.setIcon(icn)
		elif setting=="hide":
			icn=QIcon.fromTheme("view-hidden")
			btn.setText(_("Hide"))
			btn.setToolTip(_("Close accessdock"))
			btn.setIcon(icn)
		elif setting=="config":
			icn=QIcon.fromTheme("preferences")
			btn.setText(_("Settings"))
			btn.setToolTip(_("Launch accesshelper"))
			btn.setIcon(icn)
		elif setting=="read":
			icn=QIcon.fromTheme("audio-ready")
			self.readIcn=icn
			btn.setText(_("Read screen"))
			btn.setToolTip(_("Read text or image from clipboard"))
			btn.setIcon(icn)
		elif setting=="capture":
			icn=QIcon.fromTheme("desktop")
			self.captureIcn=icn
			btn.setText(_("Capture"))
			btn.setToolTip(_("Try to read screen content from screenshot"))
			btn.setIcon(icn)
		elif setting=="pointer_size":
			icn=QIcon.fromTheme("pointer")
			btn.setText(_("Pointer"))
			btn.setToolTip(_("Set mouse pointer size"))
			btn.setIcon(icn)
		elif setting=="color":
			icn=QIcon.fromTheme("preferences-desktop-screensaver")
			btn.setText(_("Filter"))
			btn.setToolTip(_("Apply a color filter"))
			btn.setIcon(icn)
		elif setting=="osk":
			icn=QIcon.fromTheme("input-keyboard")
			btn.setText(_("Keyboard"))
			btn.setToolTip(_("Show/Hide on-screen keyboard"))
			btn.setIcon(icn)
	#def _assignButton

	def closeEvent(self,event):
		event.ignore()
	#def closeEvent(self,event):

	def execute(self,*args,**kwargs):
		if isinstance(args,tuple):
			if args[0].lower()=="hide":
				sys.exit(0)
			elif args[0].lower()=="color":
				alphaDlg=alpha(alpha)
				alphaDlg.embebbed=True
				alphaDlg.move(self.coordx,self.coordy)
				alphaDlg._load_screen()
				alphaDlg.btn_ok.clicked.connect(alphaDlg.close)
				alphaDlg.btn_cancel.clicked.connect(alphaDlg.close)
				alphaDlg.btn_cancel.setShortcut("Esc")
				alphaDlg.setWindowModality(Qt.WindowModal)
				alphaDlg.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
				alphaDlg.show()
			elif args[0].lower()=="font_size":
				self._fontCursorSize("font")
			elif args[0].lower()=="pointer_size":
				self._fontCursorSize("pointer")
			elif args[0].lower()=="read":
				self._readScreen()
			elif args[0].lower()=="capture":
				self._captureScreen()
			elif args[0].lower()=="osk":
				self._showOsk()
			elif args[0].lower()=="scale":
				self._setScale()
			elif args[0].lower()=="config":
				self.hide()
				subprocess.run(["accesshelper"])
				btn=self.widgets.get("font_size")
				self._loadConfig()
				font=12
				if isinstance(self.fonts,str)==True:
					font=self.fonts.split(",")[1]
				btn.setText("{}px\nFont".format(font))
				btn=self.widgets.get("scale")
				btn.setText("{}%\nScale".format(self.xscale))
				self.show()
	#def execute

	def _setScale(self):
		dlg=QDialog()
		lay=QGridLayout()
		dlg.setLayout(lay)
		frame=QFrame()
		frame.setFrameShape(QFrame.Panel)
		lay.addWidget(frame)
		lay2 = QGridLayout(frame)
		cmbScale=QComboBox()
		cmbScale.addItem("100%")
		cmbScale.addItem("125%")
		cmbScale.addItem("150%")
		cmbScale.addItem("175%")
		cmbScale.addItem("200%")
		cmbScale.setCurrentText("{}%".format(self.xscale))
		lay2.addWidget(cmbScale,0,0,1,1)
		btnCancel=QPushButton("Cancel")
		btnCancel.clicked.connect(dlg.close)
		lay2.addWidget(btnCancel,2,0,1,1)
		btnOk=QPushButton("Apply")
		btnOk.clicked.connect(dlg.accept)
		lay2.addWidget(btnOk,2,1,1,1)
		dlg.move(self.coordx,self.coordy)
		dlg.setWindowModality(Qt.WindowModal)
		dlg.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
		change=dlg.exec()
		self.hide()
		if change:
			factor=cmbScale.currentText()
			factor=factor.replace("%","")
			scaleFactor=int(factor)/100
			self.accesshelper.setScaleFactor(scaleFactor,plasma=False,xrand=True)
			self.xscale=factor
			self.widgets["scale"].setText("{}%\nScale".format(self.xscale))
			try:
				with open("/tmp/.xscale","w") as f:
					f.write("{1}={0}".format(os.environ.get("XDG_SESSION_ID",1),self.xscale))
				os.chmod("/tmp/.xscale",0o666)
			except:
				pass
			#self.accesshelper.applyChanges()
		self.show()
	#def _setScale

	def _fontCursorSize(self,setting):
		def moreFontSize(*args):
			font=lblTest.font()
			fsize=font.pointSizeF()+1
			font.setPointSizeF(fsize)
			lblTest.setFont(font)
			self.fontSize=font
		def lessFontSize(*args):
			font=lblTest.font()
			fsize=font.pointSizeF()-1
			font.setPointSizeF(fsize)
			lblTest.setFont(font)
			self.fontSize=font
		def moreCursorSize(*args):
			pixmap=lblTest.pixmap()
			ptsize=pixmap.size().width()
			sizes.sort()
			if ptsize not in sizes:
				newptsize=32
				for size in sizes:
					newptsize=size
					if ptsize<=size:
						newptsize=size
						break

				ptsize=newptsize
				
			if ptsize<sizes[-1]:
				ptsize=sizes[sizes.index(ptsize)+1]
				pixmap=img[0].pixmap(QSize(ptsize,ptsize))
				lblTest.setPixmap(pixmap)
				cursor=QCursor(pixmap,0,0)
				dlg.setCursor(cursor)
		def lessCursorSize(*args):
			pixmap=lblTest.pixmap()
			ptsize=pixmap.size().width()
			sizes.sort()
			if ptsize not in sizes:
				newptsize=32
				for size in sizes:
					newptsize=size
					if ptsize<=size:
						newptsize=size
						break

				ptsize=newptsize
			if ptsize>sizes[0]:
				ptsize=sizes[sizes.index(ptsize)-1]
				pixmap=img[0].pixmap(QSize(ptsize,ptsize))
				lblTest.setPixmap(pixmap)
				cursor=QCursor(pixmap,0,0)
				dlg.setCursor(cursor)
			
		dlg=QDialog()
		lay=QGridLayout()
		dlg.setLayout(lay)
		frame=QFrame()
		frame.setFrameShape(QFrame.Panel)
		lay.addWidget(frame)
		lay2 = QGridLayout(frame)
		btnPlus=QPushButton("+")
		lay2.addWidget(btnPlus,0,0,1,1)
		btnMinus=QPushButton("-")
		lay2.addWidget(btnMinus,1,0,1,1)
		if str(setting)=="font":
			btnPlus.clicked.connect(moreFontSize)
			btnMinus.clicked.connect(lessFontSize)
			lblTest=QLabel("Texto de prueba")
			lblTest.setWordWrap(True)
			if self.fontSize:
				lblTest.setFont(self.fontSize)
		else:
			btnPlus.clicked.connect(moreCursorSize)
			btnMinus.clicked.connect(lessCursorSize)
			img=self.accesshelper.getPointerImage()
			ptSize=self.accesshelper.getPointerSize()
			qsizes=img[1]
			sizes=[]
			for qsize in qsizes:
				if qsize.width() not in sizes:
					sizes.append(qsize.width())
			sizes.sort()
			pixmap=img[0].pixmap(QSize(ptSize,ptSize))
			lblTest=QLabel()
			lblTest.setPixmap(pixmap)
		lay2.addWidget(lblTest,0,1,2,1,Qt.AlignCenter)
		btnCancel=QPushButton("Cancel")
		btnCancel.clicked.connect(dlg.close)
		lay2.addWidget(btnCancel,2,0,1,1)
		btnOk=QPushButton("Apply")
		btnOk.clicked.connect(dlg.accept)
		lay2.addWidget(btnOk,2,1,1,1)
		dlg.move(self.coordx,self.coordy)
		dlg.setWindowModality(Qt.WindowModal)
		dlg.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
		change=dlg.exec()
		self.hide()
		if change:
			if str(setting)=="font":
				qfont=lblTest.font()
				self._saveFont(qfont)
			else:
				themes=self.accesshelper.getCursors()
				for theme in themes:
					if "(" in theme:
						themeDesc=theme
						break
				themeDesc=themeDesc.split("(")[0].replace("(","").rstrip(" ")
				self._debug("Default cursor theme {}".format(themeDesc))
				#self.accesshelper.setCursorSize(lblTest.pixmap().size().width())
				self.accesshelper.setCursor(themeDesc,lblTest.pixmap().size().width())
			self.accesshelper.applyChanges()
		else:
			font=self.font()
			self.fontSize=font
			lblTest.setFont(font)
		self.show()

	def _saveFont(self,qfont):
		font=qfont.toString()
		self.setFont(qfont)
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
		self.widgets["font_size"].setText("{:.0f}px\nFont".format(size))

	def _readScreen(self,*args):
		self.widgets["capture"].setIcon(self.captureIcn)
		self.speaker.btn=self.widgets["read"]
		self.speaker.icn=self.widgets["read"].icon()
		if self.speaker.play==True:
			self.speaker.stop()
			self.widgets["read"].setIcon(self.readIcn)
		else:
			self.speaker.clipboard=True
			self.widgets["read"].setIcon(self.cancelIcn)
			self.speaker.start()
	#def _readScreen

	def _captureScreen(self,*args):
		self.widgets["read"].setIcon(self.readIcn)
		self.speaker.btn=self.widgets["capture"]
		self.speaker.icn=self.widgets["capture"].icon()
		self.hide()
		if self.speaker.play==True:
			self.speaker.stop()
			self.widgets["capture"].setIcon(self.captureIcn)
		else:
			self.speaker.clipboard=False
			self.widgets["capture"].setIcon(self.cancelIcn)
			self.speaker.start()
		time.sleep(2)
		self.show()
	#def _readScreen

	def _showOsk(self):
		subprocess.run(["qdbus","org.onboard.Onboard","/org/onboard/Onboard/Keyboard","org.onboard.Onboard.Keyboard.ToggleVisible"])

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
		if os.path.isfile(os.path.join(os.environ.get('HOME'),".config","accesshelper",self.confFile)):
			with open(os.path.join(os.environ.get('HOME'),".config","accesshelper",self.confFile),'r') as f:
				config.update(json.loads(f.read()))
		config["coords"]=[x,y]
		self.coordx,self.coordy=(x,y)
		with open(os.path.join(os.environ.get('HOME'),".config","accesshelper",self.confFile),'w') as f:
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
			sys.exit(0)
		except:
			kill=False

with open("/tmp/.accessdock.pid","w") as f:
	f.write("{}".format(os.getpid()))

app=QApplication(["AccessDock"])
dock=accessdock()
dock.show()
app.exec_()
