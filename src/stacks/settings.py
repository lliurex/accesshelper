#!/usr/bin/python3
from llxaccessibility import llxaccessibility
import os,json
import subprocess
from PySide6.QtWidgets import QApplication,QLabel,QGridLayout,QCheckBox,QHeaderView,QTableWidgetItem,QAbstractScrollArea,QComboBox,QPushButton,QFileDialog,QInputDialog,QTableWidget
from PySide6 import QtGui
from PySide6.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem, QTableTouchWidget, QPushInfoButton
import locale
import gettext
_ = gettext.gettext

i18n={
	"CONFIG":_("Settings"),
	"DESCRIPTION":_("Other options"),
	"DLG":_("Select accessibility profile"),
	"DOCK":_("Autostart dock"),
	"GRUB":_("Beep when computer starts"),
	"LOAD":_("Load profile"),
	"MENU":_("Other Settings"),
	"MONO":_("Mono audio"),
	"PROFILE":_("Start session with profile"),
	"PROFNME":_("Save as..."),
	"PROFDSC":_("Accesswizard profile"),
	"SAVE":_("Save current profile"),
	"SDDM_ORCA":_("Enable ORCA in login screen"),
	"SDDM_BEEP":_("Beep when login screen loads"),
	"SESSION_BEEP":_("Beep on session start"),
	"TOOLTIP":_("Advanced settings")
	}

class settings(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.setProps(shortDesc=i18n.get("MENU"),
		    description=i18n.get('DESCRIPTION'),
		    longDesc=i18n.get('DESCRIPTION'),
			icon="preferences-other",
			tooltip=i18n.get("TOOLTIP"),
			index=4,
			visible=True)
		self.enabled=True
		self.accesshelper=llxaccessibility.client()
	#def __init__

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.tblGrid=QTableTouchWidget()
		self.tblGrid.setColumnCount(2)
		self.tblGrid.setRowCount(5)
		self.tblGrid.verticalHeader().hide()
		self.tblGrid.horizontalHeader().hide()
		self.tblGrid.setSelectionBehavior(QTableWidget.SelectRows)
		self.tblGrid.setSelectionMode(QTableWidget.SingleSelection)
		self.tblGrid.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
		self.tblGrid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.tblGrid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.box.addWidget(self.tblGrid)
		self.btnAccept.clicked.connect(self.writeConfig)
		self.chkBeGr=QCheckBox(i18n["GRUB"])
		self.tblGrid.setCellWidget(0,0,self.chkBeGr)
		self.chkBeSd=QCheckBox(i18n["SDDM_BEEP"])
		self.tblGrid.setCellWidget(0,1,self.chkBeSd)
		self.chkOrSd=QCheckBox(i18n["SDDM_ORCA"])
		self.tblGrid.setCellWidget(1,0,self.chkOrSd)
		self.chkAuDo=QCheckBox(i18n["DOCK"])
		self.tblGrid.setCellWidget(2,0,self.chkAuDo)
		self.chkBeSe=QCheckBox(i18n["SESSION_BEEP"])
		self.tblGrid.setCellWidget(2,1,self.chkBeSe)
		self.chkProf=QCheckBox(i18n["PROFILE"])
		self.tblGrid.setCellWidget(3,0,self.chkProf)
		self.cmbProf=QComboBox()
		self.chkProf.clicked.connect(lambda: self.cmbProf.setEnabled(self.chkProf.isChecked()))
		self.tblGrid.setCellWidget(3,1,self.cmbProf)
		self.chkMono=QCheckBox(i18n["MONO"])
		self.tblGrid.setCellWidget(4,0,self.chkMono)
		self.btnSave=QPushButton(i18n["SAVE"])
		self.btnSave.clicked.connect(self._saveProfile)
		self.tblGrid.setCellWidget(5,0,self.btnSave)
		self.btnLoad=QPushButton(i18n["LOAD"])
		self.btnLoad.clicked.connect(self._loadProfile)
		self.tblGrid.setCellWidget(5,1,self.btnLoad)
	#def __initScreen__

	def updateScreen(self):
		config=self.readConfig()
		self.chkBeGr.setChecked(config.get("begr",False))
		self.chkBeSd.setChecked(config.get("besd",False))
		self.chkOrSd.setChecked(config.get("orsd",False))
		self.chkBeSe.setChecked(config.get("bese",False))
		self.chkAuDo.setChecked(config.get("audo",False))
		self.chkProf.setChecked(config.get("prfl",False))
		self.cmbProf.clear()
		self.cmbProf.setEnabled(self.chkProf.isChecked())
		self.chkMono.setChecked(config.get("mono",False))
		profiles=self._getProfiles()
		for p in profiles:
			self.cmbProf.addItem(p)
		self.cmbProf.setCurrentText(config.get("prin",""))
	#def updateScreen

	def _getProfiles(self):
		return(self.accesshelper.listProfiles())
	#def _getProfiles

	def _saveProfile(self,*args,pname="profile"):
		pname=QInputDialog.getText(None, i18n.get("DLG"), i18n.get("PROFNME"))[0]
		if len(pname)>0:
			self.accesshelper.saveProfile(pname)
	#def _saveProfiles

	def _loadProfile(self,*args,ppath="profile"):
		ffilter="{} (*.tar)".format(i18n.get("PROFDSC"))
		prflDir=self.accesshelper.getProfilesDir()
		ppath=QFileDialog.getOpenFileName(None, i18n.get("DLG"), prflDir,ffilter)[0]
		if os.path.exists(ppath):
			self.accesshelper.loadProfile(ppath)
	#def _loadProfiles

	def readConfig(self):
		config={}
		config["begr"]=self.accesshelper.readKFile("kaccessrc","LliurexAccessibility","beepOnGrub")
		config["besd"]=self.accesshelper.readKFile("kaccessrc","LliurexAccessibility","beepOnSddm")
		config["orsd"]=self.accesshelper.readKFile("kaccessrc","LliurexAccessibility","orcaOnSddm")
		config["bese"]=self.accesshelper.readKFile("kaccessrc","LliurexAccessibility","beepOnSession")
		config["audo"]=self.accesshelper.readKFile("kaccessrc","LliurexAccessibility","autostartDock")
		config["mono"]=self.accesshelper.readKFile("kaccessrc","LliurexAccessibility","mono")
		config["prfl"]=False
		config["prin"]=self.accesshelper.readKFile("kaccessrc","LliurexAccessibility","profileOnInit")
		if len(config["prin"])>0:
			config["prfl"]=True
		for key in config.keys():
			if config[key]=="false" or (config[key]=="" and key!="prin"):
				config[key]=False
			if config[key]=="true":
				config[key]=True
		return (config)
	#def readConfig

	def readScreen(self):
		config={}
		config["begr"]=self.chkBeGr.isChecked()
		config["bese"]=self.chkBeSe.isChecked()
		config["besd"]=self.chkBeSd.isChecked()
		config["orsd"]=self.chkOrSd.isChecked()
		config["audo"]=self.chkAuDo.isChecked()
		config["prfl"]=self.chkProf.isChecked()
		config["mono"]=self.chkMono.isChecked()
		config["prin"]=""
		if config["prfl"]==True:
			config["prin"]=self.cmbProf.currentText()
		return(config)
	#def readScreen
	
	def writeConfig(self):
		sw_grub=str(self.chkBeGr.isChecked())
		sw_sddm=str(self.chkBeSd.isChecked())
		sw_orca=str(self.chkOrSd.isChecked())
		sw_mono=str(self.chkMono.isChecked())
		config=self.readConfig()
		if sw_grub==str(config["begr"]):
			sw_grub=""
		if sw_sddm==str(config["besd"]):
			sw_sddm=""
		if sw_orca==str(config["orsd"]):
			sw_orca=""
		if sw_mono==str(config["mono"]):
			sw_mono=""
		config.update(self.readScreen())
		self.accesshelper.writeKFile("kaccessrc","LliurexAccessibility","beepOnSession",config["bese"])
		self.accesshelper.writeKFile("kaccessrc","LliurexAccessibility","autostartDock",config["audo"])
		self.accesshelper.writeKFile("kaccessrc","LliurexAccessibility","profileOnInit",config["prin"])
		self.accesshelper.writeKFile("kaccessrc","LliurexAccessibility","beepOnSddm",config["besd"])
		self.accesshelper.writeKFile("kaccessrc","LliurexAccessibility","orcaOnSddm",config["orsd"])
		self.accesshelper.writeKFile("kaccessrc","LliurexAccessibility","beepOnGrub",config["begr"])
		self.accesshelper.writeKFile("kaccessrc","LliurexAccessibility","mono",config["mono"])
		#REM
		self.accesshelper.setSessionSound(config["bese"])
		self.accesshelper.setDockEnabled(config["audo"])
		#Privileged options
		#self.accesshelper.setSDDMSound(config["sdbe"])
		if len(sw_grub+sw_sddm+sw_orca)>0:
			cmd=["pkexec","/usr/share/accesswizard/tools/enableOptions.sh",sw_grub,sw_sddm,sw_orca]
			subprocess.run(cmd)
		if len(sw_mono)>0:
			self.accesshelper.setMonoAudio(config["mono"])
				
		self.btnAccept.setEnabled(False)
		self.btnCancel.setEnabled(False)
	#def writeConfig
