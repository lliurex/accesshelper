#!/usr/bin/python3
### This library implements atspi communications
import os,shutil,sys
from spellchecker import SpellChecker
from PySide2.QtWidgets import QApplication,QMessageBox
import dbus,dbus.exceptions
from PySide2.QtGui import QClipboard
from collections import OrderedDict
import cv2
import numpy as np
import tesserocr
from PIL import Image
from orca import orca
import subprocess
from datetime import datetime
import string
import gettext
gettext.textdomain('accesswizard')
_=gettext.gettext

class clipboardManager():
	def __init__(self,*args,**kwargs):
		self.bus=True
		try:
			self.bus=dbus.Bus()
		except Exception as e:
			self.bus=False
	#def __init__(self,*args,**kwargs):

	def test(self):
		try:
			dbusObject=self.bus.get_object("org.kde.klipper","/klipper")
			dbusInterface=dbus.Interface(dbusObject,"org.kde.klipper.klipper")
		except:
			pass
	#def test

	def getContents(self):
		if self.bus==True:
			return(self._getKlipperContents())
		else:
			return(self._getClipboardContents())
	#def getContents

	def clearContents(self):
		if self.bus==True:
			return(self._clearKlipperContents())
		else:
			return(self._clearClipboardContents())

	def _getKlipperContents(self):
		dbusObject=self.bus.get_object("org.kde.klipper","/klipper")
		dbusInterface=dbus.Interface(dbusObject,"org.kde.klipper.klipper")
		contents=dbusInterface.getClipboardContents()
		return(contents)
	#def _getKlipperContents(self):

	def _clearKlipperContents(self):
		dbusObject=self.bus.get_object("org.kde.klipper","/klipper")
		dbusInterface=dbus.Interface(dbusObject,"org.kde.klipper.klipper")
		contents=dbusInterface.setClipboardContents(" ")
		return(contents)
	#def _clearKlipperContents(self):

	def _getClipboardContents(self):
		pass
	#def _getClipboardContents

	def _clearClipboardContents(self):
		pass
	#def _clearClipboardContents

class speaker():
	def __init__(self,*args,**kwargs):
		self.txtFile=kwargs.get("txtFile")#.encode('iso8859-15',"replace")
		self.stretch=float(kwargs.get("stretch",1))
		self.voice=kwargs.get("voice","kal")
		self.currentDate=kwargs.get("date","240101")
		player=kwargs.get("player","")
		if player=="vlc":
			self.player=True
		else:
			self.player=False
	#def __init__

	def run(self,txtFile=""):
		confDir=os.path.join(os.environ.get('HOME','/tmp'),".local/share/accesswizard/records")
		if os.path.exists(confDir)==False:
			os.makedirs(confDir)
		txt=txtFile
		if os.path.exists(self.txtFile):
			with open(self.txtFile,"r") as f:
				txt=f.read()
		self._runFestival(txt)
	#def run

	def _runFestival(self,txt):
		confDir=os.path.join(os.environ.get('HOME','/tmp'),".local/share/accesswizard/records")
		p=subprocess.Popen(["festival","--pipe"],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
		if self.voice.startswith("voice_")==False:
			self.voice="voice_{}".format(self.voice)
		self.voice="voice_upc_ca_mar_hts"
		p.stdin.write("({})\n".format(self.voice).encode("utf8"))
		p.stdin.write("(Parameter.set 'Duration_Stretch {})\n".format(self.stretch).encode("utf8"))
		p.stdin.write("(set! utt (Utterance Text {}))\n".format(txt).encode("iso8859-1"))
		p.stdin.write("(utt.synth utt)\n".encode("utf8"))
		p.stdin.write("(utt.save.wave utt \"/tmp/.baseUtt.wav\" \'riff)\n".encode("utf8"))
		p.communicate()
		p.terminate()
		mp3Dir=os.path.join(confDir,"mp3")
		mp3File=os.path.join(mp3Dir,"{}.mp3".format(self.currentDate))
		p=subprocess.run(["lame","/tmp/.baseUtt.wav",mp3File],stdout=subprocess.PIPE,stdin=subprocess.PIPE,stderr=subprocess.PIPE)
		#os.unlink("/tmp/.baseUtt.wav")
		msgBox=QMessageBox()
		msgTxt=_("TTS finished. Listen?")
		msgInformativeTxt=_("Image was processesed")
		msgBox.setText(msgTxt)
		msgBox.setInformativeText(msgInformativeTxt)
		msgBox.setStandardButtons(QMessageBox.Yes | QMessageBox.Cancel)
		msgBox.setDefaultButton(QMessageBox.Yes)
		ret=msgBox.exec()
		if ret==QMessageBox.Yes:
			if self.player==True:
				#self._debug("Playing {} with vlc".format(mp3))
				prc=subprocess.run(["vlc",mp3File])
			else:
				#self._debug("Playing {} with TTS Strech {}".format(mp3,self.stretch))
				prc=subprocess.run(["play",mp3File])
		return 
	#def run
#class speaker

class speechhelper():
	def __init__(self):
		self.confDir=os.path.join(os.environ.get('HOME','/tmp'),".local/share/accesswizard/records")
		self.txtDir=os.path.join(self.confDir,"txt")
		self.mp3Dir=os.path.join(self.confDir,"mp3")
		if os.path.isdir(self.txtDir)==False:
			os.makedirs(self.txtDir)
		if os.path.isdir(self.mp3Dir)==False:
			os.makedirs(self.mp3Dir)
		self.dbg=True
		#self.clibboard=clipboardManager()
		#if self.clipboard.test()==False:
		self.clipboard=QClipboard()
		self.pitch=50
		self.stretch=0
		self.setRate(1)
		self.voice="JuntaDeAndalucia_es_pa_diphone"
		self.player="vlc"
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("speech: {}".format(msg))
	#def _debug

	def setRate(self,speed):
		#3x=0.40 0x=1.40 1x=0.90
		#steps are 0.25. Between 3 and 0 there are 12 steps
		#speed/0.25=Steps from 0x. Each step=8.3
		speed=abs(float(speed)-3)
		steps=float(speed)/0.25
		self.stretch=(steps*0.083)+0.40
		#return speed
	#def _setRate

	def setVoice(self,voice):
		self.voice=voice
		if self.voice.startswith("voice_")==False:
			self.voice="voice_{}".format(self.voice)
	#def setVoice

	def setPlayer(self,player):
		if player=="vlc":
			self.player="vlc"
		else:
			self.player="tts"
	#def setVoice

	def hideDock(self):
		try:
			bus=dbus.SessionBus()
			objbus=bus.get_object("net.lliurex.accessibledock","/net/lliurex/accessibledock")
			objint=dbus.Interface(bus,"net.lliurex.accessibledock")
			if objbus.isVisible():
				objbus.toggle()
		except Exception as e:
			print(e)
			pass
	#def hideDock

	def showDock(self):
		try:
			bus=dbus.SessionBus()
			objbus=bus.get_object("net.lliurex.accessibledock","/net/lliurex/accessibledock")
			objint=dbus.Interface(bus,"net.lliurex.accessibledock")
			if objbus.isVisible()==False:
				objbus.toggle()
		except Exception as e:
			print(e)
			pass
	#def showDock


	def readScreen(self,*args,onlyClipboard=False,onlyScreen=False):
		txt=""
		if onlyScreen==False:
			txt=self._getClipboardText().strip()
		if not txt and onlyClipboard==False:
			img=self._getImgForOCR(onlyClipboard,onlyScreen)
			imgPIL=None
			if os.path.isfile(img):
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
		prc=0
		if txt:
			self._invokeReader(txt)
		app.quit()

		return(prc)
	#def readScreen

	def _getClipboardText(self):
		txt=""
		txt=self.clipboard.text(self.clipboard.Selection)
		txt=txt.strip()
		#if not txt:
		#	txt=self.clipboard.text()
		#self._debug("Read selection: {}".format(txt))
		return(txt)
	#def _getClipboardText

	def _getClipboardImg(self):
		self._debug("Taking Screenshot to clipboard")
		self.hideDock()
		subprocess.run(["spectacle","-a","-b","-c"])
		img=self.clipboard.image()
		buffer = QBuffer()
		buffer.open(QBuffer.ReadWrite)
		img.save(buffer, "PNG")
		return(buffer)
	#def _getClipboardImg

	def _getImgForOCR(self,onlyClipboard=False,onlyScreen=False):
		outImg="/tmp/out.png"
		img=None
		if onlyScreen==False:
			img=self.clipboard.image()
		if img:
			self._debug("Reading clipboard IMG")
			img.save(outImg, "PNG")
		else:
			if onlyScreen==False:
				img=self.clipboard.pixmap()
			if img:
				self._debug("Reading clipboard PXM")
				img.save(outImg, "PNG")
			elif onlyClipboard==False:
				self.hideDock()
				self._debug("Taking Screenshot")
				subprocess.run(["spectacle","-a","-e","-b","-c","-o",outImg])
		return(outImg)
	#def _getImgForOCR

	def _invokeReader(self,txt):
		currentDate=datetime.now()
		fileName="{}.txt".format(currentDate.strftime("%Y%m%d_%H%M%S"))
		txtFile=os.path.join(self.txtDir,fileName)
		txt=txt.replace("\"","\'")
		with open(txtFile,"w") as f:
			f.write("\"{}\"".format(txt))
		self._debug("Generating with Strech {}".format(self.stretch))
		prc=self.readFile(txtFile,currentDate)
		while len(self.clipboard.text(self.clipboard.Selection))>0:
			self.clipboard.clear(self.clipboard.Selection)
			self.clipboard.clear()
			cmd=["qdbus","org.kde.klipper","/klipper","org.kde.klipper.klipper.setClipboardContents"," "]
			subprocess.run(cmd)
		QApplication.exit()
		app.quit
		return(prc)
	#def _invokeReader

	def readFile(self,txtFile,currentDate):
		if isinstance(currentDate,str)==False:
			currentDate=currentDate.strftime("%Y%m%d_%H%M%S")
		self._debug("Date type {}".format(type(currentDate)))
		spk=speaker(txtFile=txtFile,stretch=self.stretch,voice=self.voice,date=currentDate,player=self.player)
		spk.run()
		self.showDock()
	#	try:
	#		prc=subprocess.Popen(["python3",self.libfestival,txt,str(self.stretch),self.voice,currentDate,self.player])
	#	except:
	#		print("Aborted")
	#	prc.communicate()
	#	return(prc)

	def _spellCheck(self,txt):
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
		return(txt)
	#def _spellCheck

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
			self._debug((api.AllWordConfidences()))
		#txt=tesserocr.image_to_text(imgPIL,lang="spa")
		txt=self._spellCheck(txt)
		return(txt)

	def _processImg(self,img):
		outImg="{}".format(img)
		image=cv2.imread(img,flags=cv2.IMREAD_COLOR)
		h, w, c = image.shape
		#self._debug(f'Image shape: {h}H x {w}W x {c}C')

		image=self.cvGrayscale(image)
	#	image = image[:, :, 0]

#		image=self.sobel(image)
#		image=self.thresholding(image)
#		image=self.cvDeskew(image)
#		image=self.opening(image)
#		image=self.smooth(image)
#		image=self.cvCanny(image)
		self._debug("Saving processed img as {}".format(outImg))
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

	def getFestivalVoices(self):
		voices={}
		voicesFolder="/usr/share/festival/voices/"
		if os.path.isdir(voicesFolder):
			for lang in os.listdir(voicesFolder):
				voices[lang]=os.listdir(os.path.join(voicesFolder,lang))
		return(voices)
	#def getFestivalVoices

	def getTtsFiles(self):
		ttsDir=os.path.join(os.environ.get('HOME'),".config/accesshelper/tts")
		allDict={}
		if os.path.isdir(ttsDir)==True:
			mp3Dir=os.path.join(ttsDir,"mp3")
			txtDir=os.path.join(ttsDir,"txt")
			txtDict={}
			mp3Dict={}
			for f in os.listdir(mp3Dir):
				if f.endswith(".mp3") and "_" in f:
					mp3Dict[f.replace(".mp3","")]=f
			for f in os.listdir(txtDir):
				if f.endswith(".txt") and "_" in f:
					txtDict[f.replace(".txt","")]=f
			for key,item in mp3Dict.items():
				allDict[key]={"mp3":item}
			for key,item in txtDict.items():
				if allDict.get(key):
					allDict[key].update({"txt":item})
				else:
					allDict[key]={"txt":item}
		ordDict=OrderedDict(sorted(allDict.items(),reverse=True))
		return(ordDict)
#class speechhelper
with open("/tmp/d","w") as f:
	f.write("OOEOEO\n")
app=QApplication(["TTS"])
spk=speechhelper()
spk.readScreen()
