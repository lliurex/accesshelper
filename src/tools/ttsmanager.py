#!/usr/bin/python3
import sys
import os,json
import shutil
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QComboBox,QHeaderView,QFileDialog,QScrollArea,QFrame
from PySide2 import QtGui
from PySide2 import QtMultimedia
from PySide2.QtCore import Qt,QSignalMapper,QSize,QThread,QObject,Signal,QUrl,QFile, QIODevice
from PySide2.QtUiTools import QUiLoader
from QtExtraWidgets import QTableTouchWidget,QKdeConfigWidget
import gettext
gettext.textdomain("accesswizard")
_ = gettext.gettext
import subprocess
from llxaccessibility import llxaccessibility
QString=type("")

i18n={
	"CONFIG":_("Screen reader"),
	"DESCRIPTION":_("TTS settings"),
	"ENGLISH":_("English"),
	"EXPORT":_("Files exported to"),
	"FILE":_("File"),
	"FILES":_("Recorded file list"),
	"KO":_("Cancel"),
	"MENUDESCRIPTION":_("Text-To-Speech related options"),
	"OK":_("Accept"),
	"PITCH":_("Pitch"),
	"RATE":_("Rate"),
	"RECORD":_("Mp3"),
	"SAVE":_("Save"),
	"SPANISH":_("Spanish"),
	"STRETCH":_("Stretch factor"),
	"SYNTH":_("Use synthesizer"),
	"TEXT":_("Text"),
	"TOOLTIP":_("Some options related with TTS"),
	"TTSINTERNAL":_("Use internal TTS"),
	"TTSORCA":_("Use ORCA"),
	"TTSVLC":_("Use VLC player"),
	"VALCAT":_("Valencian-Catalan"),
	"VOICE":_("Voice")
	}

class playSignal(QObject):
	sig = Signal(str)
#class playSignal

class playFile(QThread):
	def __init__(self,ttsFile,parent=None):
		QThread.__init__(self, parent)
		self.player=QtMultimedia.QMediaPlayer()
		content=QtMultimedia.QMediaContent(QUrl.fromLocalFile(ttsFile))
		self.player.setMedia(content)
		self.signal = playSignal()
		self.start = True
	#def __init__

	def run(self):
		self.player.play()
		self.player.stateChanged.connect(self.stopPlay)
	#def run

	def stopPlay(self):
		if self.start==True:
			self.player.stop()
			self.signal.sig.emit('OK')
		self.start = False
	#def stopPlay
#class playFile

class ttshelper(QWidget):
	def __init__(self):
		self.dbg=False
		QWidget.__init__(self)
		self._debug("tts Load")
		self.accesshelper=llxaccessibility.client()
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.tooltip=i18n.get('TOOLTIP')
		self.mp3BtnDict={}
		self.playing=[]
		self.voiceMap={}
	#def __init__

	def _debug(self,msg=""):
		if self.dbg:
			print("tts: {}".format(msg))
	#def _debug

	def _loadConfigScreenFromScript(self):
		candidateFiles=[os.path.join(os.environ.get("HOME",""),".local","share","kwin","scripts","ocrwindow","contents","ui","config.ui"),"/usr/share/kwin/scripts/ocrwindow/contents/ui/config.ui"]
		uiFile=""
		for candidate in candidateFiles:
			if os.path.exists(candidate):
				uiFile=candidate
				break
		if len(uiFile)==0:
			return
		return(QKdeConfigWidget.QKdeConfigWidget(uiFile))
	#def _loadConfigScreenFromScript(self):

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		box=QGridLayout()
		wdg=QWidget()
		wdg.setLayout(box)
		scr=QScrollArea()
		self.box.addWidget(scr,0,0,1,2)
		lbl=QLabel(i18n.get("CONFIG"))
		box.addWidget(lbl,0,0,1,1)
		self.wdgConfig=self._loadConfigScreenFromScript()
		box.addWidget(self.wdgConfig,1,0,1,2)
		frm=QFrame()
		frm.setFrameShape(frm.HLine)
		box.addWidget(frm,4,0,1,2)
		lblFiles=QLabel(i18n.get("FILES"))
		box.addWidget(lblFiles,5,0,1,1,Qt.AlignLeft)
		btnReload=QPushButton()
		refreshIcon=QtGui.QIcon.fromTheme("view-refresh")
		btnReload.setIcon(refreshIcon)
		btnReload.setIconSize(QSize(24,24))
		btnReload.clicked.connect(self.updateScreen)
		box.addWidget(btnReload,5,1,1,1,Qt.AlignRight)
		self.tblFiles=QTableTouchWidget()
		self.tblFiles.verticalHeader().setVisible(False)
		box.addWidget(self.tblFiles,6,0,1,2)
		scr.setWidget(wdg)
		scr.setWidgetResizable(True)
		scr.horizontalScrollBar().hide()
		btnOk=QPushButton(i18n.get("OK"))
		btnOk.clicked.connect(self.writeConfig)
		btnKo=QPushButton(i18n.get("KO"))
		btnKo.clicked.connect(sys.exit)
		hbox=QGridLayout()
		wdg=QWidget()
		wdg.setLayout(hbox)
		self.box.addWidget(wdg,1,1,1,1)
		hbox.addWidget(btnOk,0,0,1,1)
		hbox.addWidget(btnKo,0,1,1,1)
		self.updateScreen()
	#def _load_screen

	def _resetScreen(self):
		#self.cmbVoice.clear()
		#self.cmbRate.clear()
		#self.cmbPitch.clear()
		#self.cmbSynth.clear()
		self.tblFiles.setRowCount(0)
		self.tblFiles.setColumnCount(4)
		self.tblFiles.setHorizontalHeaderLabels([i18n.get("FILE"),i18n.get("RECORD"),i18n.get("TEXT"),i18n.get("SAVE")])
		self.tblFiles.setAlternatingRowColors(True)
	#def _resetScreen

	def _getDataFromFname(self,fname):
		dateKey=fname.split("_")[0]
		dateKey=dateKey[0:4]+"/"+dateKey[4:6]+"/"+dateKey[6:8]
		timeKey=fname.split("_")[1]
		timeKey=timeKey[0:2]+":"+timeKey[2:4]+":"+timeKey[4:6]
		return(dateKey,timeKey)
	#def _getDataFromFname

	def _populateFileList(self):
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._processTtsFile)
		iconSize=QSize(64,64)
		btnSize=QSize(128,72)
		icons={"mp3":QtGui.QIcon.fromTheme("media-playback-start"),"txt":QtGui.QIcon.fromTheme("document-open"),"sav":QtGui.QIcon.fromTheme("document-save")}
		self._debug("Populating file list")
		fileDict=self.accesshelper.getTtsFiles()
		for fname,fdata in fileDict.items():
			row=self.tblFiles.rowCount()
			self.tblFiles.insertRow(row)
			dateKey,timeKey=self._getDataFromFname(fname)
			lbl=QLabel("{}_{}".format(dateKey,timeKey))
			self.tblFiles.setCellWidget(row,0,lbl)
			btn=""
			col=1
			for component in ["mp3","txt"]:
				if fdata.get(component,"")!="":
					extension=".{}".format(component)
					icon=icons.get(component)
					btn=self._newBtn(icon,extension,fname,iconSize,btnSize,sigmap_run,self.tblFiles)
					self.tblFiles.setCellWidget(row,col,btn)
					col+=1
			if col>1:
				btn=self._newBtn(icons["sav"],"",fname,iconSize,btnSize,sigmap_run,self.tblFiles)
				self.tblFiles.setCellWidget(row,len(component),btn)
		self.tblFiles.resizeColumnsToContents()
		self.tblFiles.resizeRowsToContents()
		self.tblFiles.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
		self.tblFiles.setMinimumWidth(btnSize.width()*(0.9+self.tblFiles.columnCount()))
	#def _populateFileList

	def updateScreen(self):
		config=self._readConfig()
		rate=config.get('rate','1')
		rate+="x"
		pitch=config.get('pitch','50')
		stretch=config.get('stretch','50')
		voice=config.get('voice','')
		synth=config.get('synth','true')
		self._resetScreen()
		self._populateFileList()
	#def _udpate_screen

	def _newBtn(self,icon,extension,key,iconSize,btnSize,sigmap_run,widget):
		btn=QPushButton(icon,"")
		self.mp3BtnDict.update({"{}{}".format(key,extension):btn})
		btn.setIconSize(iconSize)
		btn.setFixedSize(btnSize)
		setmap="{0}{1}".format(key,extension)
		sigmap_run.setMapping(btn,setmap)
		btn.clicked.connect(sigmap_run.map)
		return(btn)
	#def _newBtn

	def _processTtsFile(self,ttsFile):
		confDir=os.path.join(os.environ.get('HOME','/tmp'),".local/share/accesswizard/records")
		self._debug("Opening {}".format(ttsFile))
		if ttsFile.endswith(".mp3"):
			btn=self.mp3BtnDict.get(ttsFile)
			if os.path.exists(ttsFile)==False:
				ttsFile=os.path.join(confDir,"mp3",ttsFile)
			self._playFile(ttsFile,btn)
		elif ttsFile.endswith(".txt"):
			if os.path.exists(ttsFile)==False:
				ttsFile=os.path.join(confDir,"txt",ttsFile)
			subprocess.run(["kwrite",ttsFile])
		else:
			destDir=QFileDialog.getExistingDirectory()
			if destDir:
				self._debug("Exporting {0} to {1}".format(ttsFile,destDir))
				mp3File="{}.mp3".format(ttsFile)
				if os.path.exists(mp3File)==False:
					mp3Path=os.path.join(confDir,"mp3",mp3File)
				txtFile="{}.txt".format(ttsFile)
				if os.path.exists(txtFile)==False:
					txtPath=os.path.join(confDir,"txt",txtFile)
				shutil.copy(mp3Path,os.path.join(destDir,os.path.basename(mp3File)))
				shutil.copy(txtPath,os.path.join(destDir,os.path.basename(txtFile)))
				#self.showMsg("{} {}".format(i18n.get("EXPORT"),destDir))
	#def _processTtsFile

	def _playFile(self,ttsFile,btn):
		skip=False
		if len(self.playing)>0:
			if btn==self.playing[0]:
				skip=True
			self.playThread.stopPlay()
		if len(self.playing)==0 and skip==False:
			self.playing.append(btn)
			self.playThread=playFile(ttsFile)
			self.playThread.signal.sig.connect(lambda:(self._stopPlay(btn)))
			mp3Icon=QtGui.QIcon.fromTheme("media-playback-stop")
			btn.setIcon(mp3Icon)
			self.playThread.run()
	#def _playFile

	def _stopPlay(self,btn):
		if btn in self.playing:
			self.playing.pop(self.playing.index(btn))
		mp3Icon=QtGui.QIcon.fromTheme("media-playback-start")
		btn.setIcon(mp3Icon)
	#def _stopPlay

	def _readScreen(self):
		data={}
		#data["voice"]=self.voiceMap.get(self.cmbVoice.currentText(),self.cmbVoice.currentText().replace(" ","_"))
		#data["rate"]=self.cmbRate.currentText().replace("x","")
		##data["pitch"]=self.cmbPitch.currentText()
		#data["pitch"]="1"
		#data["stretch"]=self.cmbstretch.currentText()
		synt=self.cmbSynth.currentText()
		if self.cmbSynth.currentText==i18n.get("TTSINTERNAL"):
			data["synth"]="false"
		else:
			data["synth"]="true"
		return(data)
	#def _readScreen

	def _readConfig(self,*args):
		#Data is provided from kwin-script ocrwindow
		data={}
		for field in ["voice","rate","pitch","synth","stretch","orca","vlc"]:
			cmd=["kreadconfig5","--file","kwinrc","--group","Script-ocrwindow","--key",field.capitalize()]
			out=subprocess.check_output(cmd,universal_newlines=True,encoding="utf8")
			data[field]=out.strip()
		return(data)
	#def _readConfig

	def writeConfig(self):
		self.wdgConfig.saveChanges()
		#config=self._readConfig()
		#data=self._readScreen()
		#Data is saved to kwin-script ocrwindow
		#config.update(data)
		#for field,value in config.items():
		#	self.accesshelper.writeKFile("kwinrc","Script-ocrwindow",field.capitalize(),value)
		#return(config)
	#def writeConfig
#class ttshelper

if __name__=="__main__":
	app=QApplication(["TTS Manager"])
	config=ttshelper()
	config.__initScreen__()
	pwd=os.path.dirname(os.path.abspath(__file__))
	icnPath=os.path.join(pwd,"rsrc/ttsmanager.png")
	icn=QtGui.QIcon(icnPath)
	app.setDesktopFileName(icnPath.replace(".png",".desktop"))
	config.setWindowIcon(icn)
	config.show()
	config.setMinimumHeight(config.sizeHint().height()*1.2)
	config.setMinimumWidth(config.sizeHint().width()*1.2)
	#config.updateScreen()
	app.exec_()
