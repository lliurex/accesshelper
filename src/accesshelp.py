#!/usr/bin/env python3
import sys
import subprocess
import os
import json
from PySide2.QtWidgets import QApplication,QMessageBox,QGridLayout,QLabel,QPushButton
from PySide2.QtCore import Qt
from appconfig.appConfigScreen import appConfigScreen as appConfig
from stacks import libaccesshelper
import gettext
import time
_ = gettext.gettext
gettext.textdomain('accesshelper')


wrkDirList=["/usr/share/accesshelper/profiles","/usr/share/accesshelper/default",os.path.join(os.environ.get("HOME",''),".config/accesshelper/profiles")]
accesshelper=libaccesshelper.accesshelper()

HLP_USAGE=_("usage: accesshelper [--set profile]|[--list]")
HLP_NOARGS=_("With no args launch accesshelper GUI")
HLP_SET=_("--set [profile]: Activate specified profile.\n\tCould be an absolute path or a profile from default profiles path")
HLP_LIST=_("--list: List available profiles")
ERR_WRKDIR=_("could not be accessed")
ERR_NOPROFILE=_("There's no profiles at")
ERR_LOADPROFILE=_("Error loading")
ERR_SETPROFILE=_("Must select one from:")
MSG_LOADPROFILE=_("Loading profile")
MSG_REBOOT=_("It's recommended to logout from session now\nin order of avoid inconsistencies")
MSG_LOGOUT=_("Logout")
MSG_LATER=_("Later")
MSG_AUTOSTARTDISABLED=_("Profile not loaded: Autostart is disabled")
MSG_PROFILELOADED=_("Profile loaded")

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
	QApplication.quit()
	accesshelper.applyChanges()
#def _restartSession

def showDialog(*args):
	if os.path.isfile(configChanged)==False:
		return
	os.remove(configChanged)
	msg=MSG_REBOOT
	msgTitle=MSG_LOGOUT
	dlgClose=QMessageBox(QMessageBox.Warning,msgTitle,msg)
	dlgClose.setStandardButtons(QMessageBox.Ok|QMessageBox.Ignore)
	layout=QGridLayout()
	lbl=QLabel()
	layout.addWidget(lbl,0,0,1,2)
	btnRestart=QPushButton(MSG_LOGOUT)
	btnRestart.clicked.connect(_restartSession)
	layout.addWidget(btnRestart,1,0,1,1,Qt.AlignCenter)
	btnLater=QPushButton(MSG_LATER)
	btnLater.clicked.connect(QApplication.quit)
	#layout.addWidget(btnLater,1,1,1,1,Qt.AlignCenter)
	dlgClose.setLayout(layout)
	if dlgClose.exec()==QMessageBox.Ok:
		_restartSession()
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
	if os.path.isfile(configChanged):
		os.remove(configChanged)
	app=QApplication(["AccessHelper"])
	app.aboutToQuit.connect(showDialog)
	config=appConfig("AccessHelper",{'app':app})
	config.setRsrcPath("/usr/share/accesshelper/rsrc")
	config.setIcon('accesshelper')
	config.setWiki('https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Accesibilidad-en-Lliurex:-Accesshelper')
	config.setBanner('access_banner.png')
	#config.setBackgroundImage('repoman_login.svg')
	config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':os.path.join(os.environ['HOME'],".config/accesshelper")},confFile="accesshelper.json")
	config.Show()
	config.setFixedSize(config.width(),config.height())
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

