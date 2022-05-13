#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QComboBox,QTableWidget,QHeaderView
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper
from appconfig.appConfigStack import appConfigStack as confStack
import gettext
_ = gettext.gettext
import json
import subprocess
from stacks import libaccesshelper
from stacks import libspeechhelper
QString=type("")

i18n={
	"CONFIG":_("Configuration"),
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
	"RECORD":_("Recording"),
	"TEXT":_("Text File")
	}

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
		self.index=11
		self.enabled=True
		self.changed=[]
		self.level='user'
		self.config={}
		self.optionChanged=[]
	#def __init__

	def _load_screen(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.widgets={}
		self.level='user'
		self.config=self.getConfig(level=self.level)
		config=self.config.get(self.level,{})
		lblVoice=QLabel(i18n.get("VOICE"))
		self.box.addWidget(lblVoice,0,0,1,1)
		cmbVoice=QComboBox()
		self.widgets.update({"voice":cmbVoice})
		self.box.addWidget(cmbVoice,0,1,1,1)
		lblSpeed=QLabel(i18n.get("SPEED"))
		self.box.addWidget(lblSpeed,1,0,1,1)
		cmbSpeed=QComboBox()
		self.widgets.update({"speed":cmbSpeed})
		self.box.addWidget(cmbSpeed,1,1,1,1)
		lblPitch=QLabel(i18n.get("PITCH"))
		self.box.addWidget(lblPitch,2,0,1,1)
		cmbPitch=QComboBox()
		self.widgets.update({"pitch":cmbPitch})
		self.box.addWidget(cmbPitch,2,1,1,1)
		lblSynt=QLabel(i18n.get("SYNT"))
		self.box.addWidget(lblSynt,3,0,1,1)
		cmbSynt=QComboBox()
		self.widgets.update({"synt":cmbSynt})
		self.box.addWidget(cmbSynt,3,1,1,1)
		lblFiles=QLabel(i18n.get("FILES"))
		self.box.addWidget(lblFiles,4,0,1,2,Qt.AlignLeft)
		tblFiles=QTableWidget()
		tblFiles.verticalHeader().setVisible(False)
		self.widgets.update({"files":tblFiles})
		self.box.addWidget(tblFiles,5,0,1,2)
		self.updateScreen()
	#def _load_screen

	def updateScreen(self):
		config=self.getConfig(self.level)
		speed=config[self.level].get('speed','1x')
		pitch=config[self.level].get('pitch','50')
		voice=config[self.level].get('voice','')
		synt=config[self.level].get('synth','internal')
		for key,widget in self.widgets.items():
			if isinstance(widget,QComboBox):
				widget.clear()
			elif isinstance(widget,QTableWidget):
				widget.setRowCount(0)
				widget.setColumnCount(3)
				widget.setHorizontalHeaderLabels([i18n.get("FILE"),i18n.get("RECORD"),i18n.get("TEXT")])
			if key=="voice":
				self._debug("Getting installed voices")
				for i in self.accesshelper.getFestivalVoices():
					widget.addItem(i)
			if key=="speed":
				self._debug("Setting speed values")
				i=0
				while i<=3:
					if isinstance(i,float):
						if i.is_integer():
							i=int(i)
					widget.addItem("{}x".format(str(i)))
					i+=0.25
				widget.setCurrentText(speed)
			if key=="pitch":
				self._debug("Setting pitch values")
				for i in range (1,101):
					widget.addItem(str(i))
				widget.setCurrentText(pitch)
			if key=="synt":
				self._debug("Setting synt values")
				widget.addItem(i18n.get("INTERNALTTS"))
				widget.addItem(i18n.get("VLCTTS"))
				if synt=="vlc":
					widget.setCurrentText(i18n.get("VLCTTS"))
			if key=="files":
				self._populateFileList(widget)
	#def _udpate_screen

	def _populateFileList(self,widget):
		sigmap_run=QSignalMapper(self)
		sigmap_run.mapped[QString].connect(self._processTtsFile)
		mp3Icon=QtGui.QIcon.fromTheme("media-playback-start")
		txtIcon=QtGui.QIcon.fromTheme("document-open")
		self._debug("Populating file list")
		fileDict=self.accesshelper.getTtsFiles()
		for key,files in fileDict.items():
			row=widget.rowCount()
			widget.insertRow(row)
			lbl=QLabel(key)
			widget.setCellWidget(row,0,lbl)
			btn=""
			if files.get("mp3",None):
				btn=QPushButton(mp3Icon,"")
				widget.setCellWidget(row,1,btn)
				sigmap_run.setMapping(btn,"{}.mp3".format(key))
				btn.clicked.connect(sigmap_run.map)
			if files.get("txt",None):
				btn=QPushButton(txtIcon,"")
				widget.setCellWidget(row,2,btn)
				sigmap_run.setMapping(btn,"{}.txt".format(key))
				btn.clicked.connect(sigmap_run.map)
		widget.resizeColumnsToContents()
		widget.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)

	def _processTtsFile(self,ttsFile):
		confDir=os.path.join(os.environ.get('HOME','/tmp'),".config/accesshelper/tts")
		if ttsFile.endswith(".mp3"):
			self.speech.readFile(os.path.join(confDir,"mp3",ttsFile))
		elif ttsFile.endswith(".txt"):
			subprocess.run(["scite",os.path.join(confDir,"txt",ttsFile)])
	#def _processTtsFile

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		return

