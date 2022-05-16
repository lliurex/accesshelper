#!/usr/bin/python3
### This library implements atspi communications
#import pyatspi
#import festival
import os,shutil
from spellchecker import SpellChecker
from PySide2.QtGui import QClipboard
import cv2
import numpy as np
import tesserocr
from PIL import Image
import subprocess
from datetime import datetime
from multiprocessing import Process

class speechhelper():
	def __init__(self):
		self.dbg=True
		self.confDir=os.path.join(os.environ.get('HOME','/tmp'),".config/accesshelper")
		self.txtDir=os.path.join(self.confDir,"tts/txt")
		self.mp3Dir=os.path.join(self.confDir,"tts/mp3")
		if os.path.isdir(self.txtDir)==False:
			os.makedirs(self.txtDir)
		if os.path.isdir(self.mp3Dir)==False:
			os.makedirs(self.mp3Dir)
		#self.tts=festival
		self.clipboard=QClipboard()
		self.pitch=50
		self.stretch=0
		self.setRate(1)
		#eSpeak min speed=80 max speed=390
		self.voice="JuntaDeAndalucia_es_pa_diphone"
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("speech: {}".format(msg))
	#def _debug

	def setRate(self,speed):
		#3x=0.40 0x=1.40 1x=0.90
		#steps are 0.25. Between 3 and 0 there are 12 steps
		#speed/0.25=Steps from 0x. Each step=8.3
		speed=abs(int(speed)-3)
		steps=float(speed)/0.25
		self.stretch=(steps*0.083)+0.40
		#return speed
	#def _setRate

	def setVoice(self,voice):
		self.voice=voice
		if self.voice.startswith("voice_")==False:
			self.voice="voice_{}".format(self.voice)
	#def setVoice

	def readScreen(self,*args):
		txt=self._getClipboardText()
		print("???????????????????")
		print(txt)
		print("???????????????????")
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
		currentDate=datetime.now()
		fileName="{}.txt".format(currentDate.strftime("%Y%m%d_%H%M%S"))
		txtFile=os.path.join(self.txtDir,fileName)
		if self.dbg:
			with open(txtFile,"w") as f:
				f.write("\"{}\"".format(txt))
		self._debug("Generating with Strech {}".format(self.stretch))
		print("***************")
		print(txt)
		print("***************")
		#self.tts.setStretchFactor(self.stretch)
		self.readFile(txtFile,currentDate)
	#	tts=Process(target=self.readFile,args=(txtFile,currentDate,))
	#	tts.start()
	#	tts.join()
	#def _invokeReader

	def readFile(self,txt,currentDate):
		print("***************")
		print(txt)
		print("***************")
		#festival.setStretchFactor(self.stretch)
		subprocess.run(["python3","/home/juanma/git/accesshelper/src/stacks/libfestival.py",txt,str(self.stretch),self.voice,currentDate.strftime("%Y%m%d_%H%M%S")])
#		import festival
#		festival.setStretchFactor(0.4)
#		mp3=festival.textToMp3File(txt)
#		mp3File="{}.mp3".format(currentDate.strftime("%Y%m%d_%H%M%S"))
#		shutil.move(mp3,os.path.join(self.mp3Dir,mp3File))
#		mp3=os.path.join(self.mp3Dir,mp3File)
#		player=False
#		if player==True:
#			self._debug("Playing {} with vlc".format(mp3))
#			subprocess.run(["vlc",mp3])
#		else:
#			self._debug("Playing {} with TTS Strech {}".format(mp3,self.stretch))
#			subprocess.run(["play",mp3])

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
		self._debug(f'Image shape: {h}H x {w}W x {c}C')

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

