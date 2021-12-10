#!/usr/bin/env python3
import sys
import os
from PySide2.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig
from stacks import functionHelper as functionHelper

wrkDir="/usr/share/accesshelper/profiles"

def showHelp():
	print("usage: accesshelper [--set profile]|[--list]")
	print("")
	print("With no args launch accesshelper GUI")
	print("--set profile: Activate specified profile.\n\tCould be an absolute path or a profile from default profiles' path")
	print("--list: List available profiles")
	print("")

def listProfiles():
	if os.path.isdir(wrkDir):
		flist=[]
		try:
			flist=os.listdir(wrkDir)
		except: 
			print("{} could not be accessed".format(wrkDir))
		flist.sort()
		if len(flist)>0:
			for f in flist:
				print("* {}".format(f))
		else:
			print("There's no profiles at {}".format(wrkDir))
	else:
		print("{} not found".format(wrkDir))

def setProfile(profilePath):
	wrkDir,name=("","")
	if profilePath.endswith("/"):
		profilePath=profilePath.rstrip("/")
	if os.path.isdir(profilePath):
		wrkDir=os.path.dirname(profilePath)
		name=os.path.basename(profilePath)
	if wrkDir and name:
		functionHelper.restore_snapshot(wrkDir,name)
	else:
		print("Profile {} could not be loaded".format(profilePath))

if len(sys.argv)==1:
	app=QApplication(["AccessHelper"])
	config=appConfig("AccesHelper",{'app':app})
	config.setRsrcPath("/usr/share/accesshelper/rsrc")
	config.setIcon('accesshelper')
	#config.setWiki('https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Repoman+%28Bionic%29.')
	config.setBanner('access_banner.png')
	#config.setBackgroundImage('repoman_login.svg')
	#config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':'%s/.config'%os.environ['HOME']},confFile="accesHelper.conf")
	config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':os.path.join(os.environ['HOME'],"git/accessibility_wizard")},confFile="accesshelper.json")
	config.Show()
	#config.setFixedSize(config.width(),config.height())
	config.setFixedSize(800,600)
	app.exec_()
else:
	if sys.argv[1].lower()=="--set":
		tpl=sys.argv[2]
		if os.path.isdir(tpl):
			#call function blabla
			setProfile(tpl)
		elif os.path.isdir(os.path.join(wrkDir,tpl))==True:
			#call function blabla
			setProfile(os.path.join(wrkDir,tpl))
		else:
			showHelp()
	elif sys.argv[1].lower()=="--list":
		listProfiles()
	else:
		showHelp()
