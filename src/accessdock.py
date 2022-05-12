#!/usr/bin/python3
import os,sys,io,psutil
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
import json
import subprocess
import speechd
import string
from spellchecker import SpellChecker
from app2menu import App2Menu
import gettext
gettext.textdomain('accesshelper')
_ = gettext.gettext
QString=type("")
QInt=type(0)

class accessdock(QWidget):
	def __init__(self,*args,**kwargs):
		super().__init__()
		self.dbg=True
		self._chkDockRunning()
		self.menu=App2Menu.app2menu()
		self.confFile="accesshelper.json"
		self.confDir="/usr/share/accesshelper/"
		self.fastSettings={"color":"color","font_size":"","pointer_size":"","read":"","osk":"","config":"","hide":""}
		self.widgets={}
		self.accesshelper=libaccesshelper.accesshelper()
		self.coordx=0
		self.coordy=0
		self.rate=0
		self.pitch=50
		self.clipboard=QClipboard()
		self._loadConfig()
		self._renderGui()
		self.fontSize=None
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("dock: {}".format(msg))
	#def _debug

	def _chkDockRunning(self):
		ps=list(psutil.process_iter())
		pid=os.getpid()
		count=0
		for p in ps:
			if "accessdock" in str(p.name):
				count+=1
				if count>1:
					self._debug("Accessdock is running as pid {}".format(pid))
					sys.exit(0)
				pid=p.pid
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
			self.pitch=config.get("pitch","50")
			speed=speed.replace("x","")
			#eSpeak min speed=80 max speed=390
			self.rate=int(80+((float(speed)*310)/3))
			self._setKdeHotkey(hotkey)
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
		self.setWindowFlags(Qt.NoDropShadowWindowHint|Qt.WindowStaysOnTopHint|Qt.FramelessWindowHint)
		layout=QGridLayout()
		frame=QFrame()
		frame.setFrameShape(QFrame.Panel)
		layout.addWidget(frame)
		layout2 = QGridLayout(frame)
		col=0
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self.execute)
		maxw=0
		maxh=0
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
		self.setLayout(layout)
		self.move(self.coordx,self.coordy)
	#def _renderGui

	def _assignButton(self,setting,btn):
		if setting=="font_size":
			btn.setText("{:.0f}px\nFont".format(self.font().pointSizeF()))
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
		if change:
			if str(setting)=="font":
				qfont=lblTest.font()
				self._saveFont(qfont)
			else:
				themes=self.accesshelper.getCursors()
				for theme in themes:
					if "(" in theme and ("plasma" in theme.lower() or "actual" in theme.lower()):
						themeDesc=theme
						break
				themeDesc=themeDesc.split("(")[0].replace("(","").rstrip(" ")
				self._debug("Default cursor theme {}".format(themeDesc))
				self.accesshelper.setCursor(themeDesc)
				self.accesshelper.setCursorSize(lblTest.pixmap().size().width())
			self.hide()
			self.accesshelper.applyChanges()
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
		self.hide()
		txt=self._getClipboardText()
		if not txt:
			img=self._getImgForOCR()
			if img:
				imgPIL=None
				img=self._processImg(img)
				try:
					imgPIL = Image.open(img)
					self._debug("Opened IMG. Waiting OCR")
				except Exception as e:
					print(e)
					try:
						buffer=self.getClipboardImg()
						imgPIL = Image.open(io.BytesIO(buffer.data()))
					except Exception as e:
						print(e)
			if imgPIL:
				txt=self._readImg(imgPIL)
				self.clipboard.clear()
		if txt:
			self._invokeReader(txt,player=True)
			self.clipboard.clear()
			self.clipboard.clear(self.clipboard.Selection)
		self.show()
	#def _readScreen
	
	def _getClipboardText(self):
		txt=self.clipboard.text(self.clipboard.Selection)
		txt=txt.strip()
		if not txt:
			txt=self.clipboard.text()
		self._debug("Read selection: {}".format(txt))
		return(txt)
	#def _getClipboardText

	def _getClipboardImg(self):
		self._debug("Taking Screenshot to clipboard")
		subprocess.run(["spectacle","-a","-b","-c"])
		img=self.clipboard.image()
		buffer = QBuffer()
		buffer.open(QBuffer.ReadWrite)
		img.save(buffer, "PNG")
		return(buffer)
	#def _getClipboardImg

	def _getImgForOCR(self):
		outImg="/tmp/out.png"
		img=self.clipboard.image()
		if img:
			self._debug("Reading clipboard IMG")
			img.save(outImg, "PNG")
		else:
			img=self.clipboard.pixmap()
			if img:
				self._debug("Reading clipboard PXM")
				img.save(outImg, "PNG")
			else:
				self._debug("Taking Screenshot")
				subprocess.run(["spectacle","-a","-e","-b","-c","-o",outImg])
		return(outImg)
	#def _getImgForOCR

	def _invokeReader(self,txt,player):
		spell=SpellChecker(language='es')
		correctedTxt=[]
		for word in txt.split():
			word=word.replace("\"","")
			if word.capitalize().istitle():
				correctedTxt.append(spell.correction(word))
			else:
				onlytext = ''.join(filter(str.isalnum, word)) 
				if onlytext.capitalize().istitle():
					correctedTxt.append(spell.correction(onlytext))
				elif self.dbg:
					self._debug("Exclude: {}".format(word))
		txt=" ".join(correctedTxt)
		if self.dbg:
			with open("/tmp/say_accessdocker.txt","w") as f:
				f.write(txt)
		if player==True:
			subprocess.run(["speak-ng","-p","{}".format(self.pitch),"-s","{}".format(self.rate),"-v","roa/es","-w","/tmp/out.wav",txt])
			subprocess.run(["vlc","/tmp/out.wav"])
		else:
			speech=speechd.Client()
			speech.set_language("es")
			speech.set_pause_context(2)
			#eSpeak min speed=80 max speed=390
			#speechd min=-100 max=100
			#rate 155=speed 0. <155<0.>155>0

			rate=self.rate*200 #speechd scale has 200 points
			rate=rate/310 #espeak rate has 310 
			rate=rate-100
			speech.set_pitch(int(self.pitch))
			speech.set_rate(int(rate))
			txtArray=txt.split(".")
		
			for txtLine in txtArray:
				if txtLine!="":
					speech.say(txtLine)
	#def _invokeReader

	def _readImg(self,imgPIL):
		txt=""
		imgPIL=imgPIL.convert('L').resize([5 * _ for _ in imgPIL.size], Image.BICUBIC)
		imgPIL.save("/tmp/proc.png")
		with tesserocr.PyTessBaseAPI(lang="spa",psm=11) as api:
			api.ReadConfigFile('digits')
			# Consider having string with the white list chars in the config_file, for instance: "0123456789"
			whitelist=string.ascii_letters+string.digits+string.punctuation+string.whitespace
			api.SetVariable("classify_bln_numeric_mode", "0")
			#api.SetPageSegMode(tesserocr.PSM.DEFAULT)
			api.SetVariable('tessedit_char_whitelist', whitelist)
			api.SetImage(imgPIL)
			api.Recognize()
			txt=api.GetUTF8Text()
			print(api.AllWordConfidences())
		#txt=tesserocr.image_to_text(imgPIL,lang="spa")
		return(txt)

	def _processImg(self,img):
		outImg="{}".format(img)
		image=cv2.imread(img,flags=cv2.IMREAD_COLOR)
		h, w, c = image.shape
		print(f'Image shape: {h}H x {w}W x {c}C')

		image=self.cvGrayscale(image)
	#	image = image[:, :, 0]

#		image=self.sobel(image)
#		image=self.thresholding(image)
#		image=self.cvDeskew(image)
#		image=self.opening(image)
#		image=self.smooth(image)
#		image=self.cvCanny(image)
		print("Saving processed img as {}".format(outImg))
		cv2.imwrite(outImg,image)
		return(outImg)

	def opening(self,img):
		kernel = np.ones((5,5),np.uint8)
		return cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)

	def thresholding(self,image):
		return cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]


	def sobel(self,img):
		img = cv2.cvtColor(
			src=img,
			code=cv2.COLOR_RGB2GRAY,
		)

		dx, dy = 1, 0
		img_sobel = cv2.Sobel(
			src=img,
			ddepth=cv2.CV_64F,
			dx=dx,
			dy=dy,
			ksize=5,
		)
		return(img_sobel)

		 
	def morph(self,img):
		
####	op = cv2.MORPH_OPEN

####	img_morphology = cv2.morphologyEx(
####		src=img,
####		op=op,
####		kernel=np.ones((5, 5), np.uint8),
####	)
		op = cv2.MORPH_CLOSE
		img_morphology = cv2.morphologyEx(
			src=img_morphology,
			op=op,
			kernel=np.ones((5, 5), np.uint8),
		)
		return(img_morphology)
	
	# get grayscale image
	def cvGrayscale(self,image):
		return cv2.cvtColor(image, cv2.COLOR_RGB2GRAY)


	#canny edge detection
	def cvCanny(self,image):
		return cv2.Canny(image, 100, 200)

	def smooth(self,image):
		return cv2.bilateralFilter(image,9,75,75)

	def gaussian(self,image):
		img_gaussian = cv2.GaussianBlur(
			src=image,
			ksize=(5, 5),
			sigmaX=0,
			sigmaY=0,
		)
		return(img_gaussian)

	#skew correction
	def cvDeskew(self,image):
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
