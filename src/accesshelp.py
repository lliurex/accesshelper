#!/usr/bin/env python3
import sys
import os
from PySide2.QtWidgets import QApplication
from appconfig.appConfigScreen import appConfigScreen as appConfig
from stacks import functionHelper as functionHelper

wrkDirList=["/usr/share/accesshelper/profiles","/usr/share/accesshelper/profiles",os.path.join(os.environ.get("HOME",''),".config/accesshelper/profiles")]

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
		sw=functionHelper.restore_snapshot(wrkFile)
	else:
		print("Profile {} could not be loaded".format(profilePath))
	return(sw)
#def setProfile

if len(sys.argv)==1:
	app=QApplication(["AccessHelper"])
	config=appConfig("AccessHelper",{'app':app})
	config.setRsrcPath("/usr/share/accesshelper/rsrc")
	config.setIcon('accesshelper')
	#config.setWiki('https://wiki.edu.gva.es/lliurex/tiki-index.php?page=Repoman+%28Bionic%29.')
	config.setBanner('access_banner.png')
	#config.setBackgroundImage('repoman_login.svg')
	#config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':os.path.join(os.environ['HOME'],"git/accesshelper/src")},confFile="accesshelper.json")
	config.setConfig(confDirs={'system':'/usr/share/accesshelper','user':os.path.join(os.environ['HOME'],".config/accesshelper")},confFile="accesshelper.json")
	config.Show()
	#config.setFixedSize(config.width(),config.height())
	config.setFixedSize(800,600)
	app.exec_()
else:
	if sys.argv[1].lower()=="--set":
		tpl=sys.argv[2]
		if tpl.endswith(".tar")==False:
			tpl="{}.tar".format(tpl)
		#call function blabla
		if setProfile(tpl)==False:
			showHelp()
	elif sys.argv[1].lower()=="--list":
		listProfiles()
	else:
		showHelp()
