#!/usr/bin/python3
import subprocess,os
import tarfile
import tempfile
import time
import shutil
from collections import OrderedDict
from PySide2.QtGui import QIcon,QPixmap,QColor
from multiprocessing import Process
import dbus
import json
import random

class functionHelperClass():
	def __init__(self):
		self.dbg=False
		self.dictFileData={}
	#	self._initValues()
		self.tmpDir="/tmp/.accesstmp"

	def _debug(self,msg):
		if self.dbg:
			print("libhelper: {}".format(msg))
	#def _debug

	def _getMozillaSettingsFiles(self):
		mozillaFiles=[]
		mozillaDir=os.path.join(os.environ.get('HOME',''),".mozilla/firefox")
		if os.path.isdir(mozillaDir)==True:
			for mozillaF in os.listdir(mozillaDir):
				self._debug("Reading MOZILLA {}".format(mozillaF))
				fPath=os.path.join(mozillaDir,mozillaF)
				if os.path.isdir(fPath):
					self._debug("Reading DIR {}".format(mozillaF))
					if "." in mozillaF:
						self._debug("Reading DIR {}".format(mozillaF))
						prefs=os.path.join(mozillaDir,mozillaF,"prefs.js")
						if os.path.isfile(prefs):
							mozillaFiles.append(prefs)
		return mozillaFiles
	#def _getMozillaSettingsFiles

	def _getGtkSettingsFiles(self,checkExists=False):
		gtkFiles=[]
		gtkDirs=[os.path.join("/home",os.environ.get('USER',''),".config/gtk-3.0"),os.path.join("/home",os.environ.get('USER',''),".config/gtk-4.0")]
		for gtkDir in gtkDirs:
			if checkExists==False:
				gtkFiles.append(os.path.join(gtkDir,"settings.ini"))
			elif os.path.isfile(os.path.join(gtkDir,"settings.ini"))==True:
				gtkFiles.append(os.path.join(gtkDir,"settings.ini"))
		return gtkFiles
	#def _getGtkFiles

	def takeSnapshot(self,profilePath,appconfrc=''):
		home=os.environ.get("HOME")
		if appconfrc=='':
			appconfrc=os.path.join(home,".config/accesshelper/accesshelper.json")
		self._debug("Take snapshot {} {}".format(profilePath,appconfrc))
		destName=os.path.basename(profilePath)
		destDir=os.path.dirname(profilePath)
		destPath=os.path.join(destDir,destName)
		self._debug("Destination {}".format(destPath))
		#Generate tmp folders
		tmpFolder=tempfile.mkdtemp()
		#Plasma config goes to .config
		plasmaPath=os.path.join(tmpFolder,".config")
		os.makedirs(plasmaPath)
		#accesshelper to .config/accesshelper
		configPath=os.path.join(tmpFolder,".config/accesshelper")
		onboard=os.path.join(os.path.dirname(appconfrc),"onboard.dconf")
		os.makedirs(configPath)
		#autostart
		desktopStartPath=os.path.join(tmpFolder,".config/autostart")
		os.makedirs(desktopStartPath)
		autostartPath=os.path.join(home,".config","autostart")
		#autoshutdown
		desktopShutdownPath=os.path.join(tmpFolder,".config/plasma-workspace/shutdown")
		os.makedirs(desktopShutdownPath)
		autoshutdownPath=os.path.join(home,".config",".config/plasma-workspace/shutdown")
		#mozilla
		mozillaPath=os.path.join(tmpFolder,".mozilla")
		os.makedirs(mozillaPath)
		#gtk
		gtkPath=os.path.join(tmpFolder,".config")
		if os.path.isdir(gtkPath)==False:
			os.makedirs(gtkPath)

		flist=[]
		for kfile in self.dictFileData.keys():
			kPath=os.path.join(os.environ['HOME'],".config",kfile)
			if os.path.isfile(kPath):
				shutil.copy(kPath,plasmaPath)
		if os.path.isfile(appconfrc):
			shutil.copy(appconfrc,configPath)
		if os.path.isfile(onboard):
			shutil.copy(onboard,configPath)
		for auto in [autostartPath,autoshutdownPath]:
			if os.path.isdir(auto):
				for f in os.listdir(auto):
					if f.startswith("access"):
						autostart=os.path.join(auto,f)
						if auto==autostartPath:
							shutil.copy(autostart,desktopStartPath)
						else:
							shutil.copy(autostart,desktopShutdownPath)
		mozillaFiles=self._getMozillaSettingsFiles()
		for mozillaFile in mozillaFiles:
			destdir=os.path.basename(os.path.dirname(mozillaFile))
			destdir=os.path.join(mozillaPath,destdir)
			os.makedirs(destdir)
			shutil.copy(mozillaFile,destdir)
		gtkFiles=self._getGtkSettingsFiles(True)
		for gtkFile in gtkFiles:
			destdir=os.path.basename(os.path.dirname(gtkFile))
			destdir=os.path.join(gtkPath,destdir)
			os.makedirs(destdir)
			shutil.copy(gtkFile,destdir)
		(osHdl,tmpFile)=tempfile.mkstemp()
		oldCwd=os.getcwd()
		os.chdir(tmpFolder)
		with tarfile.open(tmpFile,"w") as tarFile:
			for f in os.listdir(tmpFolder):
				tarFile.add(os.path.basename(f))
		os.chdir(oldCwd)
		self._debug("Copying {0}->{1}".format(tmpFile,destPath))
		self._copyTarProfile(tmpFile,destPath)
		os.remove(tmpFile)
		return(os.path.join(destPath,os.path.basename(tmpFile)))
	#def take_snapshot

	def _copyTarProfile(self,orig,dest):
		if os.path.isdir(os.path.dirname(dest))==False:
			os.makedirs(os.path.dirname(dest))
		try:
			shutil.copy(orig,dest)
		except Exception as e:
			self._debug(e)
			cmd=["pkexec","/usr/share/accesshelper/helper/profiler.sh",orig,dest]
			try:
				pk=subprocess.run(cmd)
				if pk.returncode!=0:
					sw=False
			except Exception as e:
				self._debug(e)
				self._debug("Permission denied for {}".format(dest))
				sw=False
	#def _copyTarProfile
			
	def importExportSnapshot(self,tarFile,dest):
		self._debug(tarFile)
		if os.path.isfile(tarFile):
			if tarfile.is_tarfile(tarFile)==True:
				self._debug("Import {} to {}".format(tarFile,dest))
				self._copyTarProfile(tarFile,dest)
	#def importSnapshot

	def _checkSnapshot(self,profileTar):
		sw=False
		if os.path.isfile(profileTar):
			sw=tarfile.is_tarfile(profileTar)
		if sw==False:
			print("Error: {} is not a valid tar".format(profileTar))
		self._debug("{0} {1}".format(profileTar,sw))
		return(sw)

	def cleanHome(self,autostartFolder,autoshutdownFolder):
		self.removeAutostartDesktop("accesshelper_rgbFilter.desktop")
		for f in os.listdir(autostartFolder):
			if f.startswith("accesshelper_"):
				os.remove(os.path.join(autostartFolder,f))
		for f in os.listdir(autoshutdownFolder):
			if f.startswith("accesshelper_"):
				os.remove(os.path.join(autoshutdownFolder,f))
	#def cleanHome

	def _getOldProfile(self,profileTar,usrFolder):
		profile=profileTar
		startup="false"
		oldconf=os.path.join(usrFolder,"accesshelper.json")
		joldcontents={}
		if os.path.isfile(oldconf)==True:
			with open(oldconf,"r") as f:
				foldcontents=f.read()
			joldcontents=json.loads(foldcontents)
			if joldcontents.get("startup","")=="true":
				startup="true"
				profile=joldcontents.get("profile","")
				profile=joldcontents.get("autoprofile",profile)
		profile=os.path.basename(profile).replace(".tar","")
		return(profile,joldcontents)
	#def mergeHome

	def removeAutostartDesktop(self,desktop,folder="autostart"):
		home=os.environ.get("HOME")
		if home:
			if "shutdown" in folder:
				desktop=desktop.replace(".desktop",".sh")
			wrkFile=os.path.join(home,".config",folder,desktop)
			if os.path.isfile(wrkFile):
				os.remove(wrkFile)
	#def _removeAutostartDesktop

	def generateAutostartDesktop(self,cmd,fname,folder="autostart"):
		desktop=[]
		if "shutdown" in folder:
			if isinstance(cmd,list):
				cmd=" ".join(cmd)
			cmd="#!/bin/bash\n{}".format(cmd)
			fname=fname.replace(".desktop",".sh")
			desktop=cmd.split("\n")
		else:
			if isinstance(cmd,list):
				cmd=" ".join(cmd)
			desktop.append("[Desktop Entry]")
			desktop.append("Encoding=UTF-8")
			desktop.append("Type=Application")
			desktop.append("Name={}".format(fname.replace(".desktop","")))
			desktop.append("Comment=Apply rgb filters")
			desktop.append("Exec={}".format(cmd))
			desktop.append("StartupNotify=false")
			desktop.append("Terminal=false")
			desktop.append("Hidden=false")
		home=os.environ.get("HOME")
		if home:
			wrkFile=os.path.join(home,".config",folder,fname)
			if os.path.isdir(os.path.dirname(wrkFile))==False:
				os.makedirs(os.path.dirname(wrkFile))
			with open(wrkFile,"w") as f:
				f.write("\n".join(desktop))
			if "shutdown" in folder:
				os.chmod(wrkFile,0o755)
	#def generateAutostartDesktop

	def setOnboardConfig(self):
		home=os.environ.get("HOME")
		wrkFile=os.path.join(home,".config/accesshelper","onboard.dconf")
		if os.path.isfile(wrkFile):
			cmd=["cat",wrkFile]
			try:
				cat=subprocess.Popen(cmd,stdout=subprocess.PIPE)
			except:
				cat=None
			if cat!=None:
				cmd=["dconf","load","/org/onboard/"]
				try:
					dconf=subprocess.run(cmd,stdin=cat.stdout)
				except Exception as e:
					print(e)
				cat.communicate()
	#def setOnboardConfig
