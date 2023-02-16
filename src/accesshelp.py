#!/usr/bin/env python3
import sys
import subprocess
import os,shutil,psutil
import json
from PySide2.QtWidgets import QApplication,QDialog,QGridLayout,QLabel,QPushButton,QLayout,QSizePolicy,QDialogButtonBox
from PySide2.QtCore import Qt
from PySide2 import QtGui
from appconfig.appConfigScreen import appConfigScreen as appConfig
from stacks import libaccesshelper
from appconfig import appconfigControls
import gettext
import time
import notify2

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
MSG_APPLY=_("Changes will be applied now")
MSG_LOGOUT=_("Logout")
MSG_CHANGES=_("Options selected:")
MSG_LATER=_("Later")
MSG_AUTOSTARTDISABLED=_("Profile not loaded: Autostart is disabled")
MSG_PROFILELOADED=_("Profile loaded")
TXT_ACCEPT=_("Close Session")
TXT_APPLY=_("Apply")
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
	for pr in _getProfilesList():
		print("* {}".format(pr))
	sys.exit(0)
#def listProfiles

def _getProfilesList():
	profiles=[]
	for wrkDir in wrkDirList:
		if os.path.isdir(wrkDir):
			flist=[]
			try:
				flist=os.listdir(wrkDir)
			except: 
				profiles.append("{0} {1}".format(wrkDir,ERR_WRKDIR))
			flist.sort()
			if len(flist)>0:
				for f in flist:
					if f not in profiles and f.endswith(".tar"):
						profiles.append(f.replace(".tar",""))
			else:
				profiles.append("{0} {1}".format(ERR_NOPROFILE,wrkDir))
	return(profiles)
#def _getProfileList

def setProfile(profilePath,applyChanges=False):
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
		if applyChanges==True:
			accesshelper.applyChanges()
	else:
		print("{0} {1}".format(ERR_LOADPROFILE,profilePath))
	return(sw)
#def setProfile

def _restartSession(*args):
	accesshelper.restartSession()
	QApplication.quit()
	sys.exit(0)
#def _restartSession

def _applyChanges(*args):
	accesshelper.applyChanges()
	QApplication.quit()
	sys.exit(0)
#def _applyChanges

def _readChanges():
	changes=""
	if os.path.isfile(configChanged):
		with open(configChanged,"r") as f:
			changes=f.read()
	return(changes)
#def _readChanges

def _getStartup():
	c=config.getConfig(config.level)
	startup=c.get(config.level,{}).get("startup","false")
	sw=False
	if startup.lower()=="true":
		sw=True
	return(sw)
#def _getStartup

def _chkProfileChange(*args):
	sw=False
	listData=args[0].split()
	profiles=_getProfilesList()
	for l in listData:
		if "->" in l:
			setting=l.split("->")[-1]
			if setting.strip() in profiles:
				sw=True
	return(sw)
#def _chkProfileChange

def showDialog(*args):
	def _restoreConfig():
		cursor=QtGui.QCursor(Qt.WaitCursor)
		dlgClose.setCursor(cursor)
		home=os.environ.get('HOME')
		accesshelper.restoreSnapshot(profilePath)
		thematizer=os.path.join(home,".config/autostart/accesshelper_thematizer.desktop")
		if os.path.isfile(thematizer):
			os.remove(thematizer)
		_exit(False)
		subprocess.Popen(["/usr/share/accesshelper/accesshelp.py"])

	changes=_readChanges()
	if changes.strip()=="":
		_exit(True)
	if os.path.isfile(configChanged):
		os.remove(configChanged)
	startup=_getStartup()
	chProfile=_chkProfileChange(changes)
	msg=""
	msgTitle=MSG_LOGOUT
	dlgClose=QDialog()
	lay=QGridLayout()
	if startup==True:
		changes=_("<p><strong>Startup is enabled. Changes will not apply.\nAccesshelper will try to apply as many changes as possible for current session.\n(expect inconsistencies)</strong></p>")+changes
	elif chProfile==True:
		changes=_("<p><strong>A profile has been loaded.\nAccesshelper will try to apply as many changes as possible for current session but a session restart is required in order to apply all changes.</strong></p>")+changes
	text="{0}<br>{1}<br>".format(MSG_CHANGES,changes.replace("\n","<br>"))
	scrLabel=appconfigControls.QScrollLabel(text)
	btnOk=QPushButton(TXT_ACCEPT)
	btnOk.clicked.connect(_restartSession)
	msgReboot=MSG_REBOOT
	btnIgnore=QPushButton(TXT_IGNORE)
	btnIgnore.clicked.connect(_exit)
	btnDiscard=QPushButton(TXT_UNDO)
	btnDiscard.clicked.connect(_restoreConfig)
	if startup==True:
		btnOk=QPushButton(TXT_APPLY)
		btnOk.clicked.connect(_applyChanges)
		msgReboot=MSG_APPLY
	elif chProfile==True:
		btnOk=QPushButton(TXT_APPLY)
		btnOk.clicked.connect(_applyChanges)
		msgReboot=MSG_APPLY
		btnIgnore=QPushButton(TXT_ACCEPT)
		btnIgnore.clicked.connect(_restartSession)
		msgReboot=MSG_APPLY
	scrLabel.adjustWidth(config.sizeHint().width()/2)
	lay.addWidget(scrLabel,0,0,1,3)
	lay.addWidget(QLabel(msgReboot),1,0,1,3)
	lay.addWidget(btnOk,2,0,1,1)
	lay.addWidget(btnIgnore,2,1,1,1)
	lay.addWidget(btnDiscard,2,2,1,2)
	dlgClose.setLayout(lay)
	res=dlgClose.exec_()
#def showDialog

def _exit(quit=True):
	tmpDir="/tmp/.accesshelper"
	if os.path.isdir(tmpDir):
		shutil.rmtree(tmpDir)
	QApplication.quit()
	if quit:
		sys.exit(0)
#def _exit

##############
#### MAIN ####
##############

def _chkAppRunning():
	ps=list(psutil.process_iter())
	cont=0
	for p in ps:
		name=" ".join(p.cmdline())
		if " /usr/bin/accesshelper" in name and "python" in name:
			cont+=1
	if cont>1:
		title=_("Accesshelper running")
		notify2.init(title)
		msg=_("Can't execute another instance of Accesshelp")# is running as pid {}".format(p.pid))
		notice=notify2.Notification(msg)
		notice.show()
		QApplication.quit()
		sys.exit(0)
#def _chkAppRunning

if len(sys.argv)==1:
	_chkAppRunning()
	configChanged="/tmp/.accesshelper_{}".format(os.environ.get('USER'))
	#Take snapshot with current config
	tmpDir="/tmp/.accesshelper__{}".format(os.environ.get('USER'))
	if os.path.isdir(tmpDir):
		shutil.rmtree(tmpDir)
	os.makedirs(tmpDir)
	profilePath=accesshelper.takeSnapshot(tmpDir)
	if os.path.isfile(configChanged):
		os.remove(configChanged)
	app=QApplication(["AccessHelper"])
	app.setQuitOnLastWindowClosed(False)
	app.lastWindowClosed.connect(showDialog)
	config=appConfig("Access Helper",{'app':app})
	config.setWindowTitle("Access Helper")
	config.setRsrcPath("/usr/share/accesshelper/rsrc")
	config.setIcon('accesshelper')
	config.setWiki('https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Accesibilidad%20en%20Lliurex:%20Access%20Helper')
	config.setBanner('access_banner.png')
	config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':os.path.join(os.environ['HOME'],".config/accesshelper")},confFile="accesshelper.json")
	config.Show()
	app.exec_()
else:
	if sys.argv[1].lower()=="--set":
		applyChanges=False
		if len(sys.argv)<3:
			print("{}".format(ERR_SETPROFILE))
			listProfiles()
		if len(sys.argv)==4:
			applyChanges=False
			if sys.argv[3]=='init':
				if _getStartup()==True:
					print("{}".format(MSG_AUTOSTARTDISABLED))
					sys.exit(1)
			elif sys.argv[3]=="apply":
				applyChanges=True
		tpl=sys.argv[2]
		if tpl.endswith(".tar")==False:
			tpl="{}.tar".format(tpl)
		if setProfile(tpl,applyChanges)==False:
			showHelp()
		else:
			print("{}".format(MSG_PROFILELOADED))
	elif sys.argv[1].lower()=="--list":
		listProfiles()
	else:
		showHelp()
	QApplication.quit()
	sys.exit(0)

