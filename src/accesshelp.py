#!/usr/bin/env python3
import sys
import subprocess
import os,shutil
import json
from PySide2.QtWidgets import QApplication,QDialog,QGridLayout,QLabel,QPushButton,QLayout,QSizePolicy
from PySide2.QtCore import Qt
from PySide2 import QtGui
from appconfig.appConfigScreen import appConfigScreen as appConfig
from stacks import libaccesshelper
from appconfig import appconfigControls
import gettext
import time
_ = gettext.gettext
gettext.textdomain('access_helper')


wrkDirList=["/usr/share/accesshelper/profiles","/usr/share/accesshelper/default",os.path.join(os.environ.get("HOME",''),".config/accesshelper/profiles")]
accesshelper=libaccesshelper.accesshelper()
accesshelper.removeTmpDir()
profilePath=""
dlgClose=""

HLP_USAGE=_("usage: accesshelper [--set profile]|[--list]")
HLP_NOARGS=_("With no args launch accesshelper GUI")
HLP_SET=_("--set [profile]: Activate specified profile.\n\tCould be an absolute path or a profile from default profiles path")
HLP_LIST=_("--list: List available profiles")
ERR_WRKDIR=_("could not be accessed")
ERR_NOPROFILE=_("There's no profiles at")
ERR_LOADPROFILE=_("Error loading")
ERR_SETPROFILE=_("Must select one from:")
MSG_LOADPROFILE=_("Loading profile")
MSG_REBOOT=_("Changes will only apply after session restart")
MSG_LOGOUT=_("Logout")
MSG_CHANGES=_("Options selected:")
MSG_LATER=_("Later")
MSG_AUTOSTARTDISABLED=_("Profile not loaded: Autostart is disabled")
MSG_PROFILELOADED=_("Profile loaded")
TXT_ACCEPT=_("Close Session")
TXT_IGNORE=_("Ignore")
TXT_UNDO=_("Undo")

def showHelp():
	print(HLP_USAGE)
	print("")
	print(HLP_NOARGS)
	print(HLP_SET)
	print(HLP_LIST)
	print("")
	sys.exit(0)
#def showHelp():

def listProfiles():
	add=[]
	for wrkDir in wrkDirList:
		if os.path.isdir(wrkDir):
			flist=[]
			try:
				flist=os.listdir(wrkDir)
			except: 
				print("{0} {1}".format(wrkDir,ERR_WRKDIR))
			flist.sort()
			if len(flist)>0:
				for f in flist:
					if f not in add:
						print("* {}".format(f.rstrip(".tar")))
						add.append(f)
			else:
				print("{0} {1}".format(ERR_NOPROFILE,wrkDir))
	sys.exit(0)
#def listProfiles

def setProfile(profilePath):
	sw=False
	wrkFile=""
	for wrkDir in wrkDirList:
		if os.path.isdir(wrkDir)==True:
			fProfiles=os.listdir(wrkDir)
			if profilePath in fProfiles:
				wrkFile=os.path.join(wrkDir,profilePath)
				break
	if wrkFile:
		print("{0} {1}".format(MSG_LOADPROFILE,wrkFile))
		sw=accesshelper.restoreSnapshot(wrkFile)
	else:
		print("{0} {1}".format(ERR_LOADPROFILE,profilePath))
	return(sw)
#def setProfile

def _restartSession(*args):
#	QApplication.quit()
#	if os.path.isfile("/tmp/.set_scheme"):
#		scheme=""
#		with open("/tmp/.set_scheme","r") as f:
#			scheme=f.read()
#		if scheme:
#			accesshelper.setScheme(scheme)
#		os.remove("/tmp/.set_scheme")
#	if os.path.isfile(configChanged)==False:
	accesshelper.restartSession()
	QApplication.quit()
	sys.exit(0)
#def _restartSession

def _readChanges():
	changes=""
	if os.path.isfile(configChanged):
		with open(configChanged,"r") as f:
			changes=f.read()
	return(changes)

def showDialog(*args):
	def _restoreConfig():
		cursor=QtGui.QCursor(Qt.WaitCursor)
		dlgClose.setCursor(cursor)
		home=os.environ.get('HOME')
		accesshelper.restoreSnapshot(profilePath)
		thematizer=os.path.join(home,".config/autostart/accesshelper_thematizer.desktop")
		if os.path.isfile(thematizer):
			os.remove(thematizer)
		QApplication.quit()
		subprocess.Popen(["/usr/share/accesshelper/accesshelp.py"])
	#def _restoreConfig(self):
	changes=_readChanges()
	if changes.strip()=="":
		sys.exit(0)
	if os.path.isfile(configChanged):
		os.remove(configChanged)
	msg=""
	msgTitle=MSG_LOGOUT
	#dlgClose=QMessageBox(QMessageBox.Warning,msgTitle,msg)
	dlgClose=QDialog()
	lay=QGridLayout()
	text="{0}<br>{1}<br>".format(MSG_CHANGES,changes.replace("\n","<br>"))
	scrLabel=appconfigControls.QScrollLabel(text)
	btnOk=QPushButton(TXT_ACCEPT)
	btnOk.clicked.connect(_restartSession)
	btnIgnore=QPushButton(TXT_IGNORE)
	btnIgnore.clicked.connect(sys.exit)
	btnDiscard=QPushButton(TXT_UNDO)
	btnDiscard.clicked.connect(_restoreConfig)
	#scrLabel.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
	scrLabel.adjustWidth(config.sizeHint().width()/2)
	lay.addWidget(scrLabel,0,0,1,3)
	lay.addWidget(QLabel(MSG_REBOOT),1,0,1,3)
	lay.addWidget(btnOk,2,0,1,1)
	lay.addWidget(btnIgnore,2,1,1,1)
	lay.addWidget(btnDiscard,2,2,1,2)
	dlgClose.setLayout(lay)
	res=dlgClose.exec_()
#def showDialog


def _isAutostartEnabled():
	sysConf='/usr/share/accesshelper/accesshelper.json'
	userConf=os.path.join(os.environ['HOME'],".config/accesshelper/accesshelper.json")
	if os.path.isfile(sysConf):
		fconf=''
		with open(sysConf,'r') as f:
			fconf=json.load(f)
		if isinstance(fconf,dict):
			level=fconf.get('config','')
			autostart=fconf.get('startup','')
			if level=='user':
				with open(userConf,'r') as uf:
					ufconf=json.load(uf)
					if isinstance(ufconf,dict):
						level=fconf.get('config','')
					if level=='user':
						autostart=ufconf.get('startup','')
	sw=False
	if autostart.lower()=="true":
		sw=True
	return sw

##############
#### MAIN ####
##############

if len(sys.argv)==1:
	configChanged="/tmp/.accesshelper_{}".format(os.environ.get('USER'))
	#Take snapshot with current config
	tmpDir="/tmp/.accesshelper"
	if os.path.isdir(tmpDir):
		shutil.rmtree(tmpDir)
	os.makedirs(tmpDir)
	profilePath=accesshelper.takeSnapshot(tmpDir)
	if os.path.isfile(configChanged):
		os.remove(configChanged)
	app=QApplication(["AccessHelper"])
	app.aboutToQuit.connect(showDialog)
	#app.setQuitOnLastWindowClosed(False)
	#app.lastWindowClosed.connect(showDialog)
	config=appConfig("Access Helper",{'app':app})
	config.setWindowTitle("Access Helper")
	config.setRsrcPath("/usr/share/accesshelper/rsrc")
	config.setIcon('accesshelper')
	config.setWiki('https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Accesibilidad%20en%20Lliurex:%20Access%20Helper')
	config.setBanner('access_banner.png')
	#config.setBackgroundImage('repoman_login.svg')
	config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':os.path.join(os.environ['HOME'],".config/accesshelper")},confFile="accesshelper.json")
	config.Show()
	#config.setFixedSize(config.width(),config.height())
	app.exec_()
else:
	if sys.argv[1].lower()=="--set":
		if len(sys.argv)<3:
			print("{}".format(ERR_SETPROFILE))
			listProfiles()
		if len(sys.argv)==4:
			if sys.argv[3]=='init':
				if _isAutostartEnabled()==True:
					print("{}".format(MSG_AUTOSTARTDISABLED))
					sys.exit(1)
		tpl=sys.argv[2]
		if tpl.endswith(".tar")==False:
			tpl="{}.tar".format(tpl)
		if setProfile(tpl)==False:
			showHelp()
		else:
			print("{}".format(MSG_PROFILELOADED))
	elif sys.argv[1].lower()=="--list":
		listProfiles()
	else:
		showHelp()

