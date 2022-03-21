#!/usr/bin/python3
import os,sys,io
from PySide2.QtWidgets import QApplication,QMessageBox,QGridLayout,QLabel,QToolButton,QWidget,QFrame,QDialog,QPushButton
from PySide2.QtCore import Qt,QSignalMapper,QByteArray,QSize,QBuffer
from PySide2.QtGui import QIcon,QPixmap,QCursor,QClipboard
import dbus
import dbus.mainloop.glib
from stacks import libaccesshelper
from appconfig.appConfigStack import appConfigStack as confStack
from stacks.alpha import alpha
import cv2
import numpy as np
import tesserocr 
from PIL import Image
import gettext
import time
import json
import subprocess
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
		self.fastSettings={"color":"color","font_size":"","pointer_size":"","read":"","config":"","osk":"","hide":""}
		self.widgets={}
		self.accesshelper=libaccesshelper.accesshelper()
		self.coordx=0
		self.coordy=0
		self.clipboard=QClipboard()
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
			#lbl=QLabel(setting.replace("_"," ").capitalize())
			#layout2.addWidget(lbl,0,col,1,1)
			btn=QToolButton()
			btn.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)
			if setting=="font_size":
				btn.setText("{:.0f}\nFont".format(self.font().pointSizeF()))
			elif setting=="hide":
				icn=QIcon.fromTheme("view-hidden")
				btn.setText(_("Hide"))
				btn.setIcon(icn)
			elif setting=="config":
				icn=QIcon.fromTheme("preferences")
				btn.setText(_("Configure"))
				btn.setIcon(icn)
			elif setting=="read":
				icn=QIcon.fromTheme("audio-ready")
				btn.setText(_("Read screen"))
				btn.setIcon(icn)
			elif setting=="pointer_size":
				icn=QIcon.fromTheme("pointer")
				btn.setText(_("Pointer"))
				btn.setIcon(icn)
			elif setting=="color":
				icn=QIcon.fromTheme("preferences-desktop-screensaver")
				btn.setText(_("Filter"))
				btn.setIcon(icn)
			elif setting=="osk":
				icn=QIcon.fromTheme("input-keyboard")
				btn.setText(_("Keyboard"))
				btn.setIcon(icn)

			sigmap_run.setMapping(btn,setting)
			btn.clicked.connect(sigmap_run.map)
			layout2.addWidget(btn,0,col,1,1)
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
				self._fontCursorSize("font")
			elif args[0].lower()=="pointer_size":
				self._fontCursorSize("pointer")
			elif args[0].lower()=="read":
				self._readScreen()
			elif args[0].lower()=="osk":
				self._showOsk()
			elif args[0].lower()=="config":
				self.hide()
				subprocess.run(["accesshelper"])
				self.show()
	#def execute

	def _fontCursorSize(self,setting):
		def moreFontSize(*args):
			font=lblTest.font()
			size=font.pointSizeF()+1
			font.setPointSizeF(size)
			lblTest.setFont(font)
		def lessFontSize(*args):
			font=lblTest.font()
			size=font.pointSizeF()-1
			font.setPointSizeF(size)
			lblTest.setFont(font)
		def moreCursorSize(*args):
			pixmap=lblTest.pixmap()
			size=pixmap.size().width()
			if size in sizes:
				if size<sizes[-1]:
					size=sizes[sizes.index(size)+1]
					pixmap=img[0].pixmap(QSize(size,size))
					lblTest.setPixmap(pixmap)
					cursor=QCursor(pixmap,0,0)
					dlg.setCursor(cursor)
		def lessCursorSize(*args):
			pixmap=lblTest.pixmap()
			size=pixmap.size().width()
			if size in sizes:
				if size>sizes[0]:
					size=sizes[sizes.index(size)-1]
					pixmap=img[0].pixmap(QSize(size,size))
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
		else:
			btnPlus.clicked.connect(moreCursorSize)
			btnMinus.clicked.connect(lessCursorSize)
			img=self.accesshelper.getPointerImage()
			qsizes=img[1]
			sizes=[]
			for qsize in qsizes:
				sizes.append(qsize.width())
			sizes.sort()
			pixmap=img[0].pixmap(QSize(32,32))
			lblTest=QLabel()
			lblTest.setPixmap(pixmap)
		lay2.addWidget(lblTest,0,1,2,1)
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
		if change:
			if str(setting)=="fonts":
				qfont=lblTest.font()
				self._saveFont(qfont)
			else:
				self.accesshelper.setCursorSize(lblTest.pixmap().size().width())
				self.accesshelper.setCursor()

	def _saveFont(self,qfont):
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
		self.widgets["font_size"].setText("{:.0f}/nFont".format(size))

	def _readScreen(self,*args):
		self.hide()
		subprocess.run(["spectacle","-u","-b","-c"])
		txt=self.clipboard.text(self.clipboard.Selection)
		if not txt:
			img=self.clipboard.image()
			buffer = QBuffer()
			buffer.open(QBuffer.ReadWrite)
			img.save(buffer, "PNG")
			pil_im = Image.open(io.BytesIO(buffer.data()))
			pil_im=pil_im.convert('L').resize([3 * _ for _ in pil_im.size], Image.BICUBIC).point(lambda p: p > 75 and p + 100)
			txt=tesserocr.image_to_text(pil_im)
		self.clipboard.clear(self.clipboard.Selection)
		self.clipboard.clear()
		self.show()
		# Adding custom options
	

	# get grayscale image
	def get_grayscale(self,image):
		return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

	# noise removal
	def remove_noise(self,image):
		return cv2.medianBlur(image,5)
	 
	#thresholding
	def thresholding(self,image):
		return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

	#dilation
	def dilate(self,image):
		kernel = np.ones((5,5),np.uint8)
		return cv2.dilate(image, kernel, iterations = 1)
		
	#erosion
	def erode(self,image):
		kernel = np.ones((5,5),np.uint8)
		return cv2.erode(image, kernel, iterations = 1)

	#opening - erosion followed by dilation
	def opening(self,image):
		kernel = np.ones((5,5),np.uint8)
		return cv2.morphologyEx(image, cv2.MORPH_OPEN, kernel)

	#canny edge detection
	def canny(self,image):
		return cv2.Canny(image, 100, 200)

	#skew correction
	def deskew(self,image):
		coords = np.column_stack(np.where(image > 0))
		angle = cv2.minAreaRect(coords)[-1]
		if angle < -45:
			angle = -(90 + angle)
		else:
			angle = -angle
		(h, w) = image.shape[:2]
		center = (w // 2, h // 2)
		M = cv2.getRotationMatrix2D(center, angle, 1.0)
		rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
		return rotated

	#template matching
	def match_template(self,image, template):
		return cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED) 

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
