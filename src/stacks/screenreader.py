#!/usr/bin/python3
import sys
import os
from PySide2.QtWidgets import QApplication, QLabel, QWidget, QPushButton,QGridLayout,QComboBox,QTableWidget,QHeaderView
from PySide2 import QtGui
from PySide2.QtCore import Qt,QSignalMapper,QSize
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
	"RECORD":_("Mp3"),
	"SAVE":_("Save"),
	"TEXT":_("Text")
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
		self.widgets.update({cmbVoice:"voice"})
		self.box.addWidget(cmbVoice,0,1,1,1)
		lblSpeed=QLabel(i18n.get("SPEED"))
		self.box.addWidget(lblSpeed,1,0,1,1)
		cmbSpeed=QComboBox()
		self.widgets.update({cmbSpeed:"speed"})
		self.box.addWidget(cmbSpeed,1,1,1,1)
		lblPitch=QLabel(i18n.get("PITCH"))
		self.box.addWidget(lblPitch,2,0,1,1)
		cmbPitch=QComboBox()
		self.widgets.update({cmbPitch:"pitch"})
		self.box.addWidget(cmbPitch,2,1,1,1)
		lblSynt=QLabel(i18n.get("SYNT"))
		self.box.addWidget(lblSynt,3,0,1,1)
		cmbSynt=QComboBox()
		self.widgets.update({cmbSynt:"synt"})
		self.box.addWidget(cmbSynt,3,1,1,1)
		lblFiles=QLabel(i18n.get("FILES"))
		self.box.addWidget(lblFiles,4,0,1,2,Qt.AlignLeft)
		tblFiles=QTableWidget()
		tblFiles.verticalHeader().setVisible(False)
		self.widgets.update({tblFiles:"files"})
		self.box.addWidget(tblFiles,5,0,1,2)
		self.updateScreen()
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
				self._debug("Getting installed voices")
				for i in self.accesshelper.getFestivalVoices():
					widget.addItem(i)
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
			if files.get("mp3",None):
				btn=QPushButton(mp3Icon,"")
				widget.setCellWidget(row,1,btn)
				relFile=key
				sigmap_run.setMapping(btn,"{}.mp3".format(key))
				btn.clicked.connect(sigmap_run.map)
				btn.setIconSize(iconSize)
				btn.setFixedSize(btnSize)
			if files.get("txt",None):
				btn=QPushButton(txtIcon,"")
				widget.setCellWidget(row,2,btn)
				sigmap_run.setMapping(btn,"{}.txt".format(key))
				btn.clicked.connect(sigmap_run.map)
				btn.setIconSize(iconSize)
				btn.setFixedSize(btnSize)
			if btn:
				btn=QPushButton(saveIcon,"")
				widget.setCellWidget(row,3,btn)
				sigmap_run.setMapping(btn,"{}".format(key))
				btn.clicked.connect(sigmap_run.map)
				btn.setIconSize(iconSize)
				btn.setFixedSize(btnSize)
		widget.resizeColumnsToContents()
		widget.resizeRowsToContents()
		widget.horizontalHeader().setSectionResizeMode(0,QHeaderView.Stretch)
	#def _populateFileList

	def _processTtsFile(self,ttsFile):
		confDir=os.path.join(os.environ.get('HOME','/tmp'),".config/accesshelper/tts")
		self._debug("Opening {}".format(ttsFile))
		if ttsFile.endswith(".mp3"):
			self.speech.readFile(os.path.join(confDir,"mp3",ttsFile))
		elif ttsFile.endswith(".txt"):
			subprocess.run(["kwrite",os.path.join(confDir,"txt",ttsFile)])
	#def _processTtsFile

	def _updateConfig(self,key):
		pass

	def writeConfig(self):
		config=self.getConfig()
		for widget,desc in self.widgets.items():
			value=""
			if desc=="voice":
				value=widget.currentText()
			if desc=="speed":
				value=widget.currentText()
			if desc=="pitch":
				value=widget.currentText()
			if desc=="synt":
				value="tts"
				if "vlc" in widget.currentText().lower():
					value="vlc"
			if value!="":
				self.saveChanges(desc,value)
		f=open("/tmp/.accesshelper_{}".format(os.environ.get('USER')),'w')
		f.close()
		self.changes=""
		self.refresh=True
		return
	#def writeConfig

