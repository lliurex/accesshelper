#!/usr/bin/env python3
import sys
import subprocess
import os
import json
from PySide2.QtWidgets import QApplication,QMessageBox,QGridLayout,QLabel,QPushButton
from PySide2.QtCore import Qt
from appconfig.appConfigScreen import appConfigScreen as appConfig
from stacks import functionHelper as functionHelper
import gettext
import time
_ = gettext.gettext

wrkDirList=["/usr/share/accesshelper/profiles","/usr/share/accesshelper/default",os.path.join(os.environ.get("HOME",''),".config/accesshelper/profiles")]

def showHelp():
	print("usage: accesshelper [--set profile]|[--list]")
	print("")
	print("With no args launch accesshelper GUI")
	print("--set profile: Activate specified profile.\n\tCould be an absolute path or a profile from default profiles' path")
	print("--list: List available profiles")
	print("")
#def showHelp():

def listProfiles():
	add=[]
	for wrkDir in wrkDirList:
		if os.path.isdir(wrkDir):
			flist=[]
			try:
				flist=os.listdir(wrkDir)
			except: 
				print("{} could not be accessed".format(wrkDir))
			flist.sort()
			if len(flist)>0:
				for f in flist:
					if f not in add:
						print("* {}".format(f.rstrip(".tar")))
						add.append(f)
			else:
				print("There's no profiles at {}".format(wrkDir))
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
		print("Loading profile {}".format(wrkFile))
		sw=functionHelper.restoreSnapshot(wrkFile)
	else:
		print("Profile {} could not be loaded".format(profilePath))
	return(sw)
#def setProfile

def _restartSession(*args):
	QApplication.quit()
	cmd=["qdbus","org.kde.Shutdown","/Shutdown","logout"]
	cmd=["plasmashell","--replace"]
	subprocess.run(cmd)
	cmd=["qdbus","org.kde.KWin","/KWin","org.kde.KWin.reconfigure"]
	subprocess.run(cmd)
	#cmd=["kquitapp5","plasmashell"]
	cmd=["kcminit"]
	subprocess.run(cmd)
	#cmd=["kstart5","plasmashell"]
	#subprocess.run(cmd)
#def _restartSession

def showDialog(*args):
	if os.path.isfile(configChanged)==False:
		return
	os.remove(configChanged)
	msg=_("It's recommended to logout from session now\nin order of avoid inconsistencies")
	msgTitle=_("Logout")
	dlgClose=QMessageBox(QMessageBox.Warning,msgTitle,msg)
	dlgClose.setStandardButtons(QMessageBox.Ok|QMessageBox.Ignore)
	layout=QGridLayout()
	lbl=QLabel()
	layout.addWidget(lbl,0,0,1,2)
	btnRestart=QPushButton(_("Logout"))
	btnRestart.clicked.connect(_restartSession)
	layout.addWidget(btnRestart,1,0,1,1,Qt.AlignCenter)
	btnLater=QPushButton(_("Later"))
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
		j=''
		with open(sysConf,'r') as f:
			j=json.load(f)
		if isinstance(j,dict):
			level=j.get('config','')
			autostart=j.get('startup','')
			if level=='user':
				with open(userConf,'r') as uf:
					uj=json.load(uf)
					if isinstance(uj,dict):
						level=j.get('config','')
					if level=='user':
						autostart=j.get('startup','')
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
	#config.setWiki('https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Repoman+%28Bionic%29.')
	config.setBanner('access_banner.png')
	#config.setBackgroundImage('repoman_login.svg')
	#config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':os.path.join(os.environ['HOME'],"git/accesshelper/src")},confFile="accesshelper.json")
	config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':os.path.join(os.environ['HOME'],".config/accesshelper")},confFile="accesshelper.json")
	config.Show()
	config.setFixedSize(config.width(),config.height())
#	config.setFixedSize(800,600)
	app.exec_()
else:
	if sys.argv[1].lower()=="--set":
		if len(sys.argv)==4:
			if sys.argv[3]=='init':
				if _isAutostartEnabled()==True:
					print(_("Profile not loaded: Autostart is disabled"))
					sys.exit(1)
		tpl=sys.argv[2]
		if tpl.endswith(".tar")==False:
			tpl="{}.tar".format(tpl)
		#call function blabla
		if setProfile(tpl)==False:
			showHelp()
		else:
			print(_("Profile loaded"))
	elif sys.argv[1].lower()=="--list":
		listProfiles()
	else:
		showHelp()

