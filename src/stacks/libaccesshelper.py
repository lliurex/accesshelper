#!/usr/bin/python3
import subprocess,os
import tarfile
import tempfile
import time
import shutil
from PySide2.QtGui import QIcon,QPixmap,QColor
from multiprocessing import Process
import dbus
import json
import random
from . import libfunctionHelper 
from . import libxHelper 
from . import libplasmaHelper 
from . import libspeechhelper

class accesshelper():
	def __init__(self):
		self.dbg=False
		self.functionHelper=libfunctionHelper.functionHelperClass()
		self.xHelper=libxHelper.xHelperClass()
		self.plasmaHelper=libplasmaHelper.plasmaHelperClass()
		self.speechhelper=libspeechhelper.speechhelper()
		self.tmpDir=self.functionHelper.tmpDir
	#def __init__

	def _debug(self,msg):
		if self.dbg:
			print("libaccess: {}".format(msg))
	#def _debug

	def removeTmpDir(self):
		if os.path.isdir(self.tmpDir):
			shutil.rmtree(self.tmpDir)
			os.makedirs(self.tmpDir)
	#def removeTmpDir

	def generateChangesFile(self,window,changesDict):
		if os.path.isdir(self.tmpDir)==False:
			os.makedirs(self.tmpDir)
		destPath=os.path.join(self.tmpDir,window)
		if os.path.isdir(destPath):
			shutil.rmtree(destPath)
		os.makedirs(destPath)
		destFile=os.path.join(destPath,"{}.json".format(window))
		with open(destFile,"w") as f:
			f.writelines(changesDict)	
	#def generateChangesFile

	def getMonitors(self,*args):
		return(self.xHelper._getMonitors(*args))
	#def getMonitors

	def setOnboardConfig(self):
		return(self.functionHelper.setOnboardConfig())
	#def setOnboardConfig

	def setRGBFilter(self,*args,**kwargs):
		(xgamma,red,green,blue)=self.xHelper.setRGBFilter(*args,**kwargs)
		if len(args)==2:
			if isinstance(args[-1],bool):
				if args[-1]==False:
					self.generateAutostartDesktop(xgamma,"accesshelper_rgbFilter.desktop")
		self.plasmaHelper.setRGBFilter(red,green,blue)
		return(red,green,blue)
	#def setRGBFilter

	def removeRGBFilter(self):
		self.xHelper.removeRGBFilter()
		self.plasmaHelper.removeRGBFilter()
		self.removeAutostartDesktop("accesshelper_rgbFilter.desktop")
	#def resetRGBFilter

	def removeXscale(self):
		self.removeAutostartDesktop("accesshelper_Xscale.desktop")
	#def removeXscale

	def removeAutostartDesktop(self,desktop,folder="autostart"):
		self.functionHelper.removeAutostartDesktop(desktop,folder)
	#def _removeAutostartDesktop

	def setXscale(self,*args,**kwargs):
		cmd=self.xHelper.setXscale(*args,**kwargs)
		self.generateAutostartDesktop(cmd,"accesshelper_Xscale.desktop")
	#def setXscale(self,xscale):

	def generateAutostartDesktop(self,cmd,fname,folder="autostart"):
		self.functionHelper.generateAutostartDesktop(cmd,fname,folder)
	#def generateAutostartDesktop

	def getCursors(self):
		return(self.plasmaHelper.getCursors())
	#def getCursors

	def getCursorTheme(self):
		return(self.plasmaHelper.getCursorTheme())
	#def getCursors

	def getSchemes(self):
		return(self.plasmaHelper.getSchemes())
	#def getSchemes

	def getThemes(self):
		return(self.plasmaHelper.getThemes())
	#def getThemes

	def getCurrentTheme(self):
		current=""
		for theme in self.getThemes():
			if "(" in theme:
				current=theme
		return(current)
	#def getCurrentTheme

	def setCursor(self,*args,**kwargs):
		self.plasmaHelper.setCursor(*args,**kwargs)
	#def setCursor

	def _runSetCursorApp(self,*args):
		self.xHelper._runSetCursorApp(*args)
	#def _runSetCursorApp

	def setCursorSize(self,*args):
		self.xHelper.setCursorSize(*args)
	#def setCursorSize

	def setScheme(self,scheme):
		err=0
		try:
			subprocess.run(["plasma-apply-colorscheme",scheme],stdout=subprocess.PIPE)
		except Exception as e:
			print(e)
			err=1
		return(err)
	#def setScheme

	def setTheme(self,theme):
		err=0
		try:
			subprocess.run(["plasma-apply-desktoptheme",theme],stdout=subprocess.PIPE)
		except Exception as e:
			err=1
			print(e)
		return(err)
	#def setTheme

	def cssStyle(self,*args):
		return
		#return(self.functionHelper.cssStyle(*args))
	#def cssStyle

	def setBackgroundColor(self,*args):
		return(self.functionHelper.setBackgroundColor(*args))
	#def setBackgroundColor

	def setBackgroundImg(self,*args):
		return(self.functionHelper.setBackgroundImg(*args))
	#def setBackgroundImg

	def getBackgroundImg(self):
		#Dirt method to get wallpaper: parse plasma-org.kde.plasma.desktop-appletsrc
		confFile=os.path.join(os.environ.get("HOME",""),".config","plasma-org.kde.plasma.desktop-appletsrc")
		img=""
		if os.path.isfile(confFile):
			with open (confFile,"r") as f:
				for line in f.readlines():
					if line.startswith("Image=file://"):
						img=line.replace("Image=file://","")
						break
					elif line.startswith("Image="):
						imgFolder=line.replace("Image=","").strip()
						imgFolder=os.path.join(imgFolder,"contents/images")
						if os.path.isdir(imgFolder)==True:
							lstf=os.listdir(imgFolder)
							lstf.sort(reverse=True)
							img=os.path.join(imgFolder,lstf[random.randrange(0,len(lstf)-1)])
							break
		return img.strip()
	#def getBackgroundImg

	def getHotkey(self,*args):
		return(self.plasmaHelper.getHotkey(*args))
	#def getHotkey

	def getPlasmaConfig(self,*args):
		return(self.plasmaHelper.getPlasmaConfig(*args))
	#def getPlasmaConfig

	def setPlasmaConfig(self,*args):
		return(self.plasmaHelper.setPlasmaConfig(*args))
	#def setPlasmaConfig

	def getKdeConfigSetting(self,*args):
		return(self.plasmaHelper.getKdeConfigSetting(*args))
	#def getKdeConfigSetting

	def setKdeConfigSetting(self,*args):
		return(self.plasmaHelper.setKdeConfigSetting(*args))
	#def setKdeConfigSetting

	def takeSnapshot(self,*args,**kwargs):
		return(self.functionHelper.takeSnapshot(*args,**kwargs))
	#def takeSnapshot

	def restoreSnapshot(self,profileTar,merge=False):
		sw=self.functionHelper._checkSnapshot(profileTar)
		if sw:
			tarProfile=tarfile.open(profileTar,'r')
			tmpFolder=tempfile.mkdtemp()
			tarProfile.extractall(path=tmpFolder)
			basePath=os.path.join(tmpFolder,".config")
			self.plasmaHelper._loadPlasmaConfigFromFolder(basePath)
			confPath=os.path.join(tmpFolder,".config/accesshelper")
			jcontents={}
			desktopPath=os.path.join(tmpFolder,".config/autostart")
			if os.path.isdir(desktopPath)==True:
				autostartFolder=os.path.join(os.environ.get('HOME'),".config","autostart")
				autoshutdownFolder=os.path.join(os.environ.get('HOME'),".config","plasma-workspace/shutdown")
				if os.path.isdir(autostartFolder)==False:
					os.makedirs(autostartFolder)
				if os.path.isdir(autoshutdownFolder)==False:
					os.makedirs(autoshutdownFolder)
				#Clean operations
				self.functionHelper.cleanHome(autostartFolder,autoshutdownFolder)
				for f in os.listdir(desktopPath):
					if "profiler" in f:
						continue
					desktopFile=os.path.join(desktopPath,f)
					shutil.copy(desktopFile,autostartFolder)
			if os.path.isdir(confPath)==True:
				usrFolder=os.path.join(os.environ.get('HOME'),".config/accesshelper")
				if os.path.isdir(usrFolder)==False:
					os.makedirs(usrFolder)
				for confFile in os.listdir(confPath):
					sourceFile=os.path.join(confPath,confFile)
					self._debug("Cp {} {}".format(sourceFile,usrFolder))
					#Modify profile value.
					with open(sourceFile,"r") as f:
						fcontents=f.read()
					try:
						jcontents=json.loads(fcontents)
					except:
						jcontents.update({"profile":"{}".format(os.path.basename(profileTar))})
					(profile,oldConfig)=self.functionHelper._getOldProfile(profileTar,usrFolder)
					startup=oldConfig.get("startup","false")
					jcontents.update({"startup":startup})
					jcontents.update({"autoprofile":profile})
					if startup=="true":
						#Apply changes on startup/shutdown
						cmd="/usr/share/accesshelper/accesshelp.py --set {}".format(profile)
						self.generateAutostartDesktop(cmd,"accesshelper_profiler.desktop","plasma-workspace/shutdown")
						cmd="{} apply".format(cmd)
						self.generateAutostartDesktop(cmd,"accesshelper_profiler.desktop")
					with open(sourceFile,"w") as f:
						json.dump(jcontents,f,indent=4)
					shutil.copy(sourceFile,usrFolder)
				data=self.getPlasmaConfig()
			mozillaPath=os.path.join(tmpFolder,".mozilla")
			if os.path.isdir(mozillaPath)==True:
				mozillaFolder=os.path.join(os.environ.get('HOME'),".mozilla/firefox")
				for folder in os.listdir(mozillaPath):
					sourceFolder=os.path.join(mozillaPath,folder)
					destFolder=os.path.join(mozillaFolder,folder)
					if os.path.isdir(destFolder)==True:
						for mozillaFile in os.listdir(os.path.join(mozillaPath,folder)):
							sourceFile=os.path.join(sourceFolder,mozillaFile)
							self._debug("Cp {} {}".format(sourceFile,destFolder))
							shutil.copy(sourceFile,destFolder)
			if os.path.isdir(basePath):
				for folder in os.listdir(basePath):
					if folder.startswith('gtk') and os.path.isdir(os.path.join(basePath,folder)):
						destFolder=os.path.join(os.environ.get('HOME'),".config",folder)
						if os.path.isdir(destFolder)==False:
							os.makedirs(destFolder)
						sourceFolder=os.path.join(basePath,folder)
						for gtkFile in os.listdir(sourceFolder):
							sourceFile=os.path.join(sourceFolder,gtkFile)
							self._debug("Cp {} {}".format(sourceFile,destFolder))
							shutil.copy(sourceFile,destFolder)
			self.setNewConfig()
		return(sw)
	#def restoreSnapshot

	def importExportSnapshot(self,*args,**kwargs):
		return(self.functionHelper.importExportSnapshot(*args,**kwargs))
	#def importExportSnapshot
	
	def _getCursorTheme(self):
		return(self.functionHelper.getCursorTheme())
	#def _getCursorTheme

	def getPointerImage(self,*args,theme="default"):
		if theme=="default":
			theme=self._getCursorTheme()
		return(self.xHelper.getPointerImage(*args,theme))
	#def getPointerImage

	def getPointerSize(self,*args):
		plasmaConfig=self.getPlasmaConfig("kcminputrc")
		cursorSettings=plasmaConfig.get('kcminputrc',{}).get('Mouse',[])
		cursorSize=32
		for setting in cursorSettings:
			if isinstance(setting,tuple):
				if setting[0]=="cursorSize":
					size=setting[1]
					if not size:
						size=32
					cursorSize=int(size)
		return(cursorSize)
	#def getPointerSize

	def getTtsFiles(self):
		return(self.speechhelper.getTtsFiles())
	#def getTtsFiles

	def getFestivalVoices(self):
		return(self.speechhelper.getFestivalVoices())
	#def getFestivalVoices

	def getSettingForHotkey(self,*args):
		return(self.plasmaHelper.getSettingForHotkey(*args))
	#def getSettingForHotkey(self,*args):

	def setMozillaFirefoxFonts(self,size):
		for prefs in self.functionHelper._getMozillaSettingsFiles():
			with open(prefs,'r') as f:
				lines=f.readlines()
			newLines=[]
			for line in lines:
				if line.startswith('user_pref("font.minimum-size.x-unicode"'):
					continue
				elif line.startswith('user_pref("font.minimum-size.x-western"'):
					continue
				newLines.append(line)
			line='user_pref("font.minimum-size.x-western", {});\n'.format(size)
			newLines.append(line)
			line='user_pref("font.minimum-size.x-unicode", {});\n'.format(size)
			newLines.append(line)
			self._debug("Writting MOZILLA {}".format(prefs))
			with open(os.path.join(prefs),'w') as f:
				f.writelines(newLines)
	#def setMozillaFirefoxFonts

	def setGtkFonts(self,font):
		fontArray=font.split(',')
		gtkFont="{0}, {1} {2}".format(fontArray[0],fontArray[-1],fontArray[1])
		gtkDirs=[os.path.join("/home",os.environ.get('USER',''),".config/gtk-3.0"),os.path.join("/home",os.environ.get('USER',''),".config/gtk-4.0")]
		for gtkFile in self.functionHelper._getGtkSettingsFiles():
			fcontent=[]
			if os.path.isfile(gtkFile)==True:
				with  open(gtkFile,"r") as f:
					for line in f.readlines():
						if line.startswith("gtk-font-name")==False:
							fcontent.append(line)
			fcontent.append("gtk-font-name={}\n".format(gtkFont))
			with  open(gtkFile,"w") as f:
				try:
					f.writelines(fcontent)
				except Exception as e:
					self._debug("error saving gtk fonts")
	#def setGtkFonts

	def setGrubBeep(self,*args,**kwargs):
		self.xHelper.setGrubBeep(*args,**kwargs)
		self.plasmaHelper.setStartBeep(*args,**kwargs)
		return()
	#def setGrubBeep

	def setScaleFactor(self,*args,**kwargs):
		self.plasmaHelper.setScaleFactor(*args,**kwargs)
	#def setScaleFactor

	def currentRGBValues(self):
		return(self.xHelper.currentRGBValue())
	#def currentRGBValues

	def setHotkey(self,*args,**kwargs):
		return(self.plasmaHelper.setHotkey(*args))
	#def setHotkey

	def setThemeSchemeLauncher(self,*args,**kwargs):
		print("HELLO")
		return(self.plasmaHelper.setThemeSchemeLauncher(*args,**kwargs))
	#def setThemeSchemeLauncher

	def setNewConfig(self,*args):
		usrConfig=os.path.join(os.environ.get('HOME'),".config/accesshelper/accesshelper.json")
		if os.path.isfile(usrConfig):
			jcontent={}
			with open(usrConfig,'r') as f:
				content=f.read()
			try:
				jcontent=json.loads(content)
			except:
				fcontent=content.split("}")
				fcontent="}".join(fcontent[:-1])+"}"
				try:
					jcontent=json.loads(fcontent)
				except:
					print(fcontent)
			bkg=''
			img=''
			theme=''
			scheme=''
			color=''
			cursor=''
			size=''
			scale='100'
			xscale='100'
			dockHk=''
			grubBeep=False
			maximize=False
			alpha=[]
			for key,data in jcontent.items():
				fline=""
				if key=="bkg":
					bkg=data
				elif key=="dockHk":
					dockHk=data
				elif key=="bkgColor":
					color=data
				elif key=="background":
					img=data
				elif key=="cursor":
					cursor=data
				elif key=="cursorSize":
					size=data
				elif key=="theme":
					theme=data
				elif key=="scheme":
					scheme=data
				elif key=="scale":
					scale=data
				elif key=="xscale":
					xscale=data
				elif key=="alpha" and isinstance(data,list) and len(data)==4:
					alpha=QColor(data[0],data[1],data[2],data[3])
				elif key=="maximize":
					if data=="true":
						maximize=True
				elif key=="grubBeep":
					if data=="true":
						grubBeep=True
			if bkg=="color":
				if color:
					qcolor=QColor(color)
					self.setBackgroundColor(qcolor)
			elif bkg=="image":
				if img:
					self.setBackgroundImg(img)
			if cursor and size:
				self.setCursor(cursor,size,applyChanges=True)
			if scale:
				self.setScaleFactor(float(scale)/100)
			self.removeAutostartDesktop("accesshelper_Xscale.desktop")
			if xscale:
				if xscale.isdigit():
					self.setXscale(xscale,applyChanges=True)
			self.removeRGBFilter()
			if isinstance(alpha,QColor):
				config={'kgammarc':{'ConfigFile':[("use","kgammarc")],'SyncBox':[("sync","yes")]}}
				(red,green,blue)=self.setRGBFilter(alpha)
				values=[]
				values.append(('bgamma',"{0:.2f}".format(blue)))
				values.append(('rgamma',"{0:.2f}".format(red)))
				values.append(('ggamma',"{0:.2f}".format(green)))
				config['kgammarc'].update({'Screen 0':values})
				self.setPlasmaConfig(config)
			if theme!="":
				subprocess.run(["plasma-apply-desktoptheme",theme],stdout=subprocess.PIPE)
			if scheme!="":
				subprocess.run(["plasma-apply-colorscheme",scheme],stdout=subprocess.PIPE)
			if dockHk!="":
				self._debug("Set hotkey for dock: {}".format(dockHk))
				desc=""
				name="accessdock"
				self.setHotkey(dockHk,desc,name)
				desc="show accessdock"
				name="accessdock.desktop"
				self.setHotkey(dockHk,desc,name)
			self.plasmaHelper.setStartBeep(grubBeep)
			if maximize==True:
				config={"kwinrc":{"Windows":[("Placement","Maximizing")]}}
				self.setPlasmaConfig(config)
			else:
				config={"kwinrc":{"Windows":[("Placement","")]}}
				self.setPlasmaConfig(config)
		return()
	#def setNewConfig(self,*args):

	def applyChanges(self,setconf=True):
		if setconf:
			self.setNewConfig()
		cmd=["qdbus","org.kde.kded","/kded","unloadModule","powerdevil"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.keyboard","/modules/khotkeys","reread_configuration"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.kded","/kbuildsycoca","recreate"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.kded","/kded","reconfigure"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.plasma-desktop","/MainApplication","reparseConfiguration"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.kwin","/KWin","reconfigure"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.kded","/kded","loadModule","powerdevil"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		print("Changes applied!")
		#cmd=["kquitapp5","kglobalaccel5"]
		cmd=["qdbus","org.kde.kglobalaccel","/MainApplication","quit"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["kstart5","kglobalaccel5"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		cmd=["qdbus","org.kde.plasmashell","/PlasmaShell","refreshCurrentShell"]
		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		#cmd=["plasmashell"]
		#subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
		#cmd=["plasmashell","--replace"]
		#subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
#		cmd=["kquitapp5","kglobalaccel5"]
#		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
#		cmd=["kstart5","kglobalaccel5"]
#		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
#		cmd=["qdbus","org.kde.KWin","/KWin","org.kde.KWin.reconfigure"]
#		subprocess.run(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
	#	time.sleep(5)
	#	cmd=["pidof","plasmashell"]
	#	p=subprocess.run(cmd)
	#	if p.returncode!=0:
	#		cmd=["plasmashell"]
		#	subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
	#def _applyChangeswaitForPlasma
		
	def restartSession(self):
		cmd=["qdbus","org.kde.ksmserver","/KSMServer","org.kde.KSMServerInterface.logout","1","3","3"]
		#cmd=["qdbus","org.kde.Shutdown","/Shutdown","org.kde.Shutdown.logout"]
		subprocess.run(cmd)
	#def restartSession
