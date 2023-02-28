#!/usr/bin/python3
import sys
import os,signal
import shutil
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QComboBox,QTableWidget,QHeaderView,QFileDialog,QScrollArea
from PySide2 import QtGui
from PySide2 import QtMultimedia
from PySide2.QtCore import Qt,QSignalMapper,QSize,QThread,QObject,Signal,QUrl
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import subprocess
from stacks import libaccesshelper
from stacks import libspeechhelper
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
	"SPANISHMAN":_("Spanish man"),
	"SPANISHWOMAN":_("Spanish woman"),
	"VALENCIANWOMAN":_("Catalan woman"),
	"VALENCIANMAN":_("Catalan man")
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

class screenreader(confStack):
	def __init_stack__(self):
		self.dbg=False
		self._debug("tts Load")
		self.accesshelper=libaccesshelper.accesshelper()
		self.speech=libspeechhelper.speechhelper()
		self.menu_description=i18n.get('MENUDESCRIPTION')
		self.description=i18n.get('DESCRIPTION')
		self.icon=('preferences-desktop-text-to-speech')
		self.tooltip=i18n.get('TOOLTIP')
		self.index=7
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.config={}
		self.mp3BtnDict={}
		self.playing=[]
		self.optionChanged=[]
	#def __init__

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		box=QGridLayout()
		wdg=QWidget()
		wdg.setLayout(box)
		scr=QScrollArea()
		self.box.addWidget(scr)
		self.widgets={}
		self.level='user'
		self.config=self.getConfig(level=self.level)
		config=self.config.get(self.level,{})
		lblVoice=QLabel(i18n.get("VOICE"))
		box.addWidget(lblVoice,0,0,1,1)
		cmbVoice=QComboBox()
		self.widgets.update({cmbVoice:"voice"})
		box.addWidget(cmbVoice,0,1,1,1)
		lblSpeed=QLabel(i18n.get("SPEED"))
		box.addWidget(lblSpeed,1,0,1,1)
		cmbSpeed=QComboBox()
		self.widgets.update({cmbSpeed:"speed"})
		box.addWidget(cmbSpeed,1,1,1,1)
		lblPitch=QLabel(i18n.get("PITCH"))
		box.addWidget(lblPitch,2,0,1,1)
		cmbPitch=QComboBox()
		cmbPitch.setEnabled(False)
		self.widgets.update({cmbPitch:"pitch"})
		box.addWidget(cmbPitch,2,1,1,1)
		lblSynt=QLabel(i18n.get("SYNT"))
		box.addWidget(lblSynt,3,0,1,1)
		cmbSynt=QComboBox()
		self.widgets.update({cmbSynt:"synt"})
		box.addWidget(cmbSynt,3,1,1,1)
		lblFiles=QLabel(i18n.get("FILES"))
		box.addWidget(lblFiles,4,0,1,1,Qt.AlignLeft)
		btnReload=QPushButton()
		refreshIcon=QtGui.QIcon.fromTheme("view-refresh")
		btnReload.setIcon(refreshIcon)
		btnReload.setIconSize(QSize(24,24))
		btnReload.clicked.connect(self.updateScreen)
		box.addWidget(btnReload,4,1,1,1,Qt.AlignRight)
		tblFiles=QTableWidget()
		tblFiles.verticalHeader().setVisible(False)
		self.widgets.update({tblFiles:"files"})
		box.addWidget(tblFiles,5,0,1,2)
		scr.setWidget(wdg)
		scr.setWidgetResizable(True)
	#def _load_screen

	def updateScreen(self):
		config=self.getConfig(self.level)
		speed=config[self.level].get('speed','1x')
		pitch=config[self.level].get('pitch','50')
		voice=config[self.level].get('voice','')
		synt=config[self.level].get('synt','internal')
		for widget,desc in self.widgets.items():
			if isinstance(widget,QComboBox):
				widget.clear()
			elif isinstance(widget,QTableWidget):
				widget.setRowCount(0)
				widget.setColumnCount(4)
				widget.setHorizontalHeaderLabels([i18n.get("FILE"),i18n.get("RECORD"),i18n.get("TEXT"),i18n.get("SAVE")])
				widget.setAlternatingRowColors(True)
			if desc=="voice":
				select=""
				if "_es_pa_" in voice:
					select=i18n.get("SPANISHMAN")
				elif "_es_sf_" in voice:
					select=i18n.get("SPANISHWOMAN")
				elif "_ca_ona" in voice:
					select=i18n.get("VALENCIANWOMAN")
				elif "_ca_pau" in voice:
					select=i18n.get("VALENCIANMAN")
				else:
					select=voice
				self._debug("Getting installed voices")
				for i in self.accesshelper.getFestivalVoices():
					if "_es_pa_" in i:
						widget.addItem(i18n.get("SPANISHMAN"))
					elif "_es_sf_" in i:
						widget.addItem(i18n.get("SPANISHWOMAN"))
					elif "_ca_ona" in i:
						widget.addItem(i18n.get("VALENCIANWOMAN"))
					elif "_ca_pau" in i:
						widget.addItem(i18n.get("VALENCIANMAN"))
					else:
						widget.addItem(voice)
				widget.setCurrentText(select)
			if desc=="speed":
				self._debug("Setting speed values")
				i=0
				while i<=3:
					if isinstance(i,float):
						if i.is_integer():
							i=int(i)
					widget.addItem("{}x".format(str(i)))
					i+=0.25
				widget.setCurrentText(speed)
			if desc=="pitch":
				self._debug("Setting pitch values")
				for i in range (1,101):
					widget.addItem(str(i))
				widget.setCurrentText(pitch)
			if desc=="synt":
				self._debug("Setting synt values")
				widget.addItem(i18n.get("INTERNALTTS"))
				widget.addItem(i18n.get("VLCTTS"))
				if synt=="vlc":
					widget.setCurrentText(i18n.get("VLCTTS"))
			if desc=="files":
				self._populateFileList(widget)
	#def _udpate_screen

	def _populateFileList(self,widget):
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._processTtsFile)
		iconSize=QSize(64,64)
		btnSize=QSize(128,72)
		mp3Icon=QtGui.QIcon.fromTheme("media-playback-start")
		txtIcon=QtGui.QIcon.fromTheme("document-open")
		saveIcon=QtGui.QIcon.fromTheme("document-save")
		self._debug("Populating file list")
		fileDict=self.accesshelper.getTtsFiles()
		for key,files in fileDict.items():
			row=widget.rowCount()
			widget.insertRow(row)
			dateKey=key.split("_")[0]
			dateKey=dateKey[0:4]+"/"+dateKey[4:6]+"/"+dateKey[6:8]
			timeKey=key.split("_")[1]
			timeKey=timeKey[0:2]+":"+timeKey[2:4]+":"+timeKey[4:6]
			lbl=QLabel("{}_{}".format(dateKey,timeKey))
			widget.setCellWidget(row,0,lbl)
			btn=""
			extension=""
			if files.get("mp3",None):
				extension=".mp3"
				col=1
				icon=mp3Icon
				btn=self._newBtn(icon,extension,key,iconSize,btnSize,sigmap_run,widget)
				widget.setCellWidget(row,col,btn)
			if files.get("txt",None):
				extension=".txt"
				col=2
				icon=txtIcon
				btn=self._newBtn(icon,extension,key,iconSize,btnSize,sigmap_run,widget)
				widget.setCellWidget(row,col,btn)
			if btn:
				extension=""
				col=3
				icon=saveIcon
				btn=self._newBtn(icon,extension,key,iconSize,btnSize,sigmap_run,widget)
				widget.setCellWidget(row,col,btn)
		widget.resizeColumnsToContents()
		widget.resizeRowsToContents()
		widget.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
	#def _populateFileList

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
		confDir=os.path.join(os.environ.get('HOME','/tmp'),".config/accesshelper/tts")
		self._debug("Opening {}".format(ttsFile))
		if ttsFile.endswith(".mp3"):
			btn=self.mp3BtnDict.get(ttsFile)
			self._playFile(os.path.join(confDir,"mp3",ttsFile),btn)
		elif ttsFile.endswith(".txt"):
			subprocess.run(["kwrite",os.path.join(confDir,"txt",ttsFile)])
		else:
			destDir=QFileDialog.getExistingDirectory()
			if destDir:
				self._debug("Exporting {0} to {1}".format(ttsFile,destDir))
				mp3File="{}.mp3".format(ttsFile)
				txtFile="{}.txt".format(ttsFile)
				mp3Path=os.path.join(confDir,"mp3",mp3File)
				txtPath=os.path.join(confDir,"txt",txtFile)
				shutil.copy(mp3Path,os.path.join(destDir,mp3File))
				shutil.copy(txtPath,os.path.join(destDir,txtFile))
				self.showMsg("{} {}".format(i18n.get("EXPORT"),destDir))
	#def _processTtsFile

	def _playFile(self,ttsFile,btn):
		if btn in self.playing:
			#self.playThread.stopPlay()
			self.playThread.stopPlay()
			self.playing.pop(self.playing.index(btn))
		elif len(self.playing)==0:
			self.playing.append(btn)
			self.playThread=playFile(ttsFile)
			self.playThread.signal.sig.connect(lambda:(self._stopPlay(btn)))
			mp3Icon=QtGui.QIcon.fromTheme("media-playback-stop")
			btn.setIcon(mp3Icon)
			self.playThread.run()
	#def _playFile

	def _stopPlay(self,btn):
		mp3Icon=QtGui.QIcon.fromTheme("media-playback-start")
		btn.setIcon(mp3Icon)
	#def _stopPlay

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		config=self.getConfig()
		voice=""
		speed=""
		pitch=""
		synt=""
		for widget,desc in self.widgets.items():
			value=""
			if desc=="voice":
				value=widget.currentText()
				voice=value
				if value==i18n.get("SPANISHMAN"):
					value="JuntaDeAndalucia_es_pa_diphone"
				elif value==i18n.get("SPANISHWOMAN"):
					value="JuntaDeAndalucia_es_sf_diphone"
				elif value==i18n.get("VALENCIANWOMAN"):
					value="upc_ca_ona_hts"
				elif value==i18n.get("VALENCIANMAN"):
					value="upc_ca_pau_hts"
			if desc=="speed":
				value=widget.currentText()
				speed=value
			if desc=="pitch":
				value=widget.currentText()
				pitch=value
			if desc=="synt":
				value="tts"
				if "vlc" in widget.currentText().lower():
					value="vlc"
				synt=value
			if value!="":
				self.saveChanges(desc,value)
		self._writeFileChanges(voice,speed,pitch,synt)
	#def writeConfig
		
	def _writeFileChanges(self,voice,speed,pitch,synt):
		with open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'a') as f:
			f.write("<b>{}</b>\n".format(i18n.get("CONFIG")))
			f.write("{0}->{1}\n".format(i18n.get("VOICE"),voice))
			f.write("{0}->{1}\n".format(i18n.get("SPEED"),speed))
			f.write("{0}->{1}\n".format(i18n.get("PITCH"),pitch))
			f.write("{0}->{1}\n".format(i18n.get("SYNT"),synt))
	#def _writeFileChanges(self):
