#!/usr/bin/python3
import sys
import os,json
import shutil
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QComboBox,QTableWidget,QHeaderView,QFileDialog,QScrollArea
from PySide2 import QtGui
from PySide2 import QtMultimedia
from PySide2.QtCore import Qt,QSignalMapper,QSize,QThread,QObject,Signal,QUrl
import gettext
_ = gettext.gettext
import subprocess
from ttslib import libtts
QString=type("")

i18n={
	"CONFIG":_("Screen reader"),
	"DESCRIPTION":_("TTS settings"),
	"MENUDESCRIPTION":_("Text-To-Speech related options"),
	"TOOLTIP":_("Some options related with TTS"),
	"VOICE":_("Voice"),
	"SYNT":_("Use synthesizer"),
	"PITCH":_("Pitch"),
	"SPEED":_("Speed"),
	"FILES":_("Recorded file list"),
	"INTERNALTTS":_("Use internal TTS"),
	"VLCTTS":_("Use VLC player"),
	"FILE":_("File"),
	"RECORD":_("Mp3"),
	"SAVE":_("Save"),
	"TEXT":_("Text"),
	"EXPORT":_("Files exported to"),
	"VALCAT":_("Valencian-Catalan"),
	"SPANISH":_("Spanish"),
	"ENGLISH":_("English")
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
		self.speech=libtts.speechhelper()
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-text-to-speech')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=7
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.mp3BtnDict={}
		self.playing=[]
		self.optionChanged=[]
		self.configFile=os.path.join(os.environ.get("HOME"),".config","accessibility","ttshelper.conf")
	#def __init__

	def _debug(self,msg=""):
		if self.dbg:
			print("tts: {}".format(msg))
	#def _debug

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		box=QGridLayout()
		wdg=QWidget()
		wdg.setLayout(box)
		scr=QScrollArea()
		self.box.addWidget(scr)
		self.level='user'
		lblVoice=QLabel(i18n.get("VOICE"))
		box.addWidget(lblVoice,0,0,1,1)
		self.cmbVoice=QComboBox()
		box.addWidget(self.cmbVoice,0,1,1,1)
		lblSpeed=QLabel(i18n.get("SPEED"))
		box.addWidget(lblSpeed,1,0,1,1)
		self.cmbSpeed=QComboBox()
		box.addWidget(self.cmbSpeed,1,1,1,1)
		lblPitch=QLabel(i18n.get("PITCH"))
		box.addWidget(lblPitch,2,0,1,1)
		self.cmbPitch=QComboBox()
		self.cmbPitch.setEnabled(False)
		box.addWidget(self.cmbPitch,2,1,1,1)
		lblSynt=QLabel(i18n.get("SYNT"))
		box.addWidget(lblSynt,3,0,1,1)
		self.cmbSynth=QComboBox()
		box.addWidget(self.cmbSynth,3,1,1,1)
		lblFiles=QLabel(i18n.get("FILES"))
		box.addWidget(lblFiles,4,0,1,1,Qt.AlignLeft)
		btnReload=QPushButton()
		refreshIcon=QtGui.QIcon.fromTheme("view-refresh")
		btnReload.setIcon(refreshIcon)
		btnReload.setIconSize(QSize(24,24))
		btnReload.clicked.connect(self.updateScreen)
		box.addWidget(btnReload,4,1,1,1,Qt.AlignRight)
		self.tblFiles=QTableWidget()
		self.tblFiles.verticalHeader().setVisible(False)
		box.addWidget(self.tblFiles,5,0,1,2)
		scr.setWidget(wdg)
		scr.setWidgetResizable(True)
	#def _load_screen

	def _resetScreen(self):
		self.cmbVoice.clear()
		self.cmbSpeed.clear()
		self.cmbPitch.clear()
		self.cmbSynth.clear()
		self.tblFiles.setRowCount(0)
		self.tblFiles.setColumnCount(4)
		self.tblFiles.setHorizontalHeaderLabels([i18n.get("FILE"),i18n.get("RECORD"),i18n.get("TEXT"),i18n.get("SAVE")])
		self.tblFiles.setAlternatingRowColors(True)
	#def _resetScreen

	def _populateVoices(self):
		added=[]
		for lang,voices in self.speech.getFestivalVoices().items():
			for voice in voices:
				if voice in added:
					continue
				added.append(voice)
				text=voice.split("_")[-2]
				self.cmbVoice.addItem("{0} {1}".format(text.capitalize(),i18n.get(lang.upper())))
		self.cmbVoice.setSizeAdjustPolicy(self.cmbVoice.AdjustToContents)
		self.cmbVoice.adjustSize()
	#def _populateVoices

	def _populateSpeed(self):
		self._debug("Setting speed values")
		i=0
		while i<=3:
			if isinstance(i,float):
				if i.is_integer():
					i=int(i)
			self.cmbSpeed.addItem("{}x".format(str(i)))
			i+=0.25
		#self.cmbSpeed.setCurrentText(speed)
	#def _populateSpeed

	def _populatePitch(self):
		self._debug("Setting pitch values")
		for i in range (1,101):
			self.cmbPitch.addItem(str(i))
		self.cmbPitch.setCurrentText(pitch)
	#def _populatePitch

	def _populateSynth(self):
		self._debug("Setting synt values")
		self.cmbSynth.addItem(i18n.get("INTERNALTTS"))
		self.cmbSynth.addItem(i18n.get("VLCTTS"))
		#if synth=="vlc":
		#	self.cmbSynth.setCurrentText(i18n.get("VLCTTS"))
	#def _populateSynth(self):

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
		fileDict=self.speech.getTtsFiles()
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
	#def _populateFileList

	def updateScreen(self):
		config=self._readConfig()
		speed=config.get('speed','1x')
		pitch=config.get('pitch','50')
		voice=config.get('voice','')
		synth=config.get('synt','internal')
		self._resetScreen()
		self._populateVoices()
		self._populateSpeed()
		self._populateSynth()
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
		if btn in self.playing:
			self.playThread.stopPlay()
		elif len(self.playing)==0:
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

	def _readScreen():
		data={}
		data["voice"]=self.cmbVoice.currentText()
		data["speed"]=self.cmbSpeed.currentText()
		data["pitch"]=self.cmbPitch.currentText()
		data["synth"]=self.cmbSynth.currentText()
		return(data)
	#def _readScreen

	def _readConfig(self,*args):
		data={}
		if os.path.exists(self.configFile)==False:
			configDir=os.path.dirname(self.configFile)
			if os.path.exists(configDir)==False:
				os.makedirs(configDir)
		else:
			with open(self.configFile,"r") as f:
				data=json.loads(f.read())
		return(data)
	#def _readConfig

	def writeConfig(self):
		config=self._readConfig()
		data=self._readScreen()
		config.update(data)
		with open(self.configFile,"w") as f:
			json.dumps(config, f, indent=4)	
		return(config)
	#def writeConfig
		
	def _writeFileChanges(self,voice,speed,pitch,synt):
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			f.write("{0}->{1}\n".format(i18n.get("VOICE"),voice))
			f.write("{0}->{1}\n".format(i18n.get("SPEED"),speed))
			f.write("{0}->{1}\n".format(i18n.get("PITCH"),pitch))
			f.write("{0}->{1}\n".format(i18n.get("SYNT"),synt))
	#def _writeFileChanges(self):

if __name__=="__main__":
	app=QApplication(["TTS Manager"])
	config=ttshelper()
	config.__initScreen__()
	config.show()
	config.updateScreen()
	app.exec_()
