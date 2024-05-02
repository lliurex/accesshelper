#!/usr/bin/python3
from . import accesshelper
import os,json
from PySide2.QtWidgets import QApplication,QLabel,QGridLayout,QCheckBox,QSizePolicy,QRadioButton,QHeaderView,QTableWidgetItem,QAbstractScrollArea,QComboBox,QPushButton
from PySide2 import QtGui
from PySide2.QtCore import Qt
from QtExtraWidgets import QStackedWindowItem, QTableTouchWidget, QPushInfoButton
import locale
import gettext
_ = gettext.gettext

i18n={
	"CONFIG":_("Settings"),
	"DESCRIPTION":_("Other options"),
	"DOCK":_("Autostart dock"),
	"GRUB":_("Beep when computer starts"),
	"MENU":_("Other Settings"),
	"PROFILE":_("Start session with profile"),
	"SAVE":_("Save current profile"),
	"SDDM_ORCA":_("Enable ORCA in sddm screen"),
	"SDDM_BEEP":_("Beep when sddm launches"),
	"TOOLTIP":_("Advanced settings")
	}

class settings(QStackedWindowItem):
	def __init_stack__(self):
		self.dbg=False
		self._debug("access Load")
		self.setProps(shortDesc=i18n.get("MENU"),
		    description=i18n.get('DESCRIPTION'),
			icon="preferences-other",
			tooltip=i18n.get("TOOLTIP"),
			index=4,
			visible=True)
		self.enabled=True
		self.confDir=os.path.join(os.environ.get("HOME"),".local","share","accesswizard")
		self.confFile=os.path.join(self.confDir,"accesswizard.conf")
		self.accesshelper=accesshelper.client()
	#def __init__

	def __initScreen__(self):
		self.box=QGridLayout()
		self.setLayout(self.box)
		self.tblGrid=QTableTouchWidget()
		self.tblGrid.setColumnCount(2)
		self.tblGrid.setRowCount(4)
		self.tblGrid.verticalHeader().hide()
		self.tblGrid.horizontalHeader().hide()
		self.tblGrid.setSelectionBehavior(self.tblGrid.SelectRows)
		self.tblGrid.setSelectionMode(self.tblGrid.SingleSelection)
		self.tblGrid.setSizeAdjustPolicy(QAbstractScrollArea.AdjustToContents)
		self.tblGrid.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
		self.tblGrid.verticalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.box.addWidget(self.tblGrid)
		self.btnAccept.clicked.connect(self.writeConfig)
		self.chkGrub=QCheckBox(i18n["GRUB"])
		self.tblGrid.setCellWidget(0,0,self.chkGrub)
		self.chkDock=QCheckBox(i18n["DOCK"])
		self.tblGrid.setCellWidget(0,1,self.chkDock)
		self.chkSddm=QCheckBox(i18n["SDDM_ORCA"])
		self.tblGrid.setCellWidget(1,0,self.chkSddm)
		self.chkBeep=QCheckBox(i18n["SDDM_BEEP"])
		self.tblGrid.setCellWidget(1,1,self.chkBeep)
		self.chkProf=QCheckBox(i18n["PROFILE"])
		self.tblGrid.setCellWidget(2,0,self.chkProf)
		self.cmbProf=QComboBox()
		self.tblGrid.setCellWidget(2,1,self.cmbProf)
		self.btnSave=QPushButton(i18n["SAVE"])
		self.btnSave.clicked.connect(self._saveProfile)
		self.tblGrid.setCellWidget(3,0,self.btnSave)
	#def __initScreen__

	def updateScreen(self):
		config=self.readConfig()
		self.chkGrub.setChecked(config.get("grub",False))
		self.chkSddm.setChecked(config.get("sddm",False))
		self.chkBeep.setChecked(config.get("beep",False))
		self.chkDock.setChecked(config.get("dock",False))
		self.cmbProf.setCurrentText(config.get("profile",""))
	#def updateScreen

	def _getProfiles(self):
		profDir=os.path.join(os.environ.get("HOME"),".local","share","accesswizard","profiles")
		profiles=[]
		if os.path.exists(profDir):
			for f in os.scandir(profDir):
				profiles.append(f.path)
		return(profiles)
	#def _getProfiles

	def _saveProfile(self,*args,pname="profile"):
		print(pname)
		self.accesshelper.saveProfile(pname)
	#def _getProfiles

	def readConfig(self):
		config={}
		if os.path.exists(self.confFile):
			try:
				with open(self.confFile,"r") as f:
					config=json.loads(f.read())	
			except:
				print("Malformed {}".format(self.confFile))
		return (config)
	#def readConfig

	def readScreen(self):
		config={}
		config["grub"]=self.chkGrub.isChecked()
		config["beep"]=self.chkBeep.isChecked()
		config["sddm"]=self.chkSddm.isChecked()
		config["dock"]=self.chkDock.isChecked()
		return(config)
	#def readScreen
	
	def writeConfig(self):
		config=self.readConfig()
		config.update(self.readScreen())
		if os.path.exists(self.confDir)==False:
			os.makedirs(self.confDir)
		with open(self.confFile,"w") as f:
			json.dump(config,f,indent=4)
	#def writeConfig
